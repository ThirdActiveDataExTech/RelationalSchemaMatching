import os
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb  # type: ignore
from numpy.typing import NDArray
from pandas._typing import Scalar  # type: ignore

from app.src.correlations.enums import MatchingModel, Strategy
from app.src.correlations.relation_features import create_feature_matrix_inference
from app.src.util import time_logger


@time_logger
def schema_matching(
        l_table: pd.DataFrame, r_table: pd.DataFrame, model: MatchingModel, strategy: Strategy,
        threshold: Optional[float] = None
):
    """두 테이블로 스키마 매칭을 수행합니다.

    Args:
        l_table: l_table DataFrame
        r_table: r_table DataFrame
        model: Schema Matching XGBoost Model
        strategy: matching strategy. Check app.src.correlations.enums.Strategy.
        threshold: correlation value threshold.

    Returns:
        schema matching result
    """
    # make 2 features.
    # 1. self features for each tables
    # 2. relational features
    # TODO: separate 2 step?
    features = create_feature_matrix_inference(l_table, r_table)

    # exact predict w XGBoost model
    preds, pred_labels_list = predict_inference(features, model, threshold)

    # post process
    df_pred = postprocess_pred(l_table, r_table, preds)

    # calculate metrics
    df_pred_labels = get_pred_labels(l_table, r_table, df_pred, pred_labels_list, strategy)
    predicted_tuples = get_predicted_tuples(df_pred, df_pred_labels)

    return df_pred, df_pred_labels, predicted_tuples


def predict_inference(
        features: NDArray[Any], model: MatchingModel, threshold: Optional[float] = None
) -> Tuple[List[NDArray[Any]], List[NDArray[Any]]]:
    """Load model and predict on features using GPU if available."""
    preds = []
    pred_labels_list = []
    model_files = os.listdir(model.path)
    model_cnt = len(model_files) // 2

    # Check if GPU is available
    device = "cuda" if xgb.build_info().get("USE_CUDA", False) else "cpu"

    for i in range(model_cnt):
        bst = xgb.Booster({"nthread": 4})  # Init model
        model_file = os.path.join(model.path, f"{i}.model")
        bst.load_model(model_file)
        bst.set_param({"device": device})

        # use specified threshold or model best threshold
        if threshold is not None:
            best_threshold = float(threshold)
        else:
            threshold_file = os.path.join(model.path, f"{i}.threshold")
            with open(threshold_file, "r") as f:
                best_threshold = float(f.read())

        # Create DMatrix with GPU support if available
        labels = np.ones(len(features))
        dtest = xgb.DMatrix(features, label=labels)

        # Predict using GPU if available
        pred = bst.predict(dtest)
        pred_labels = np.where(pred > best_threshold, 1, 0)

        # Booster 가 결합된 feature 로 predict, 현재 분리 불가
        preds.append(pred)
        pred_labels_list.append(pred_labels)
        del bst

    return preds, pred_labels_list


def postprocess_pred(table1_df: pd.DataFrame, table2_df: pd.DataFrame, preds: List[NDArray[Any]]) -> pd.DataFrame:
    """원본 데이터셋과 매칭 결과를 결합해 반환합니다."""
    # do flatten and get mean
    preds = np.mean(np.array(preds), axis=0)

    # read column names
    df1_cols = table1_df.columns
    df2_cols = table2_df.columns

    # create pred_labels_matrix from preds
    # flatten and reshape to (l_table, r_table)
    preds_matrix = np.array(preds).reshape(len(df1_cols), len(df2_cols))

    df_pred = pd.DataFrame(preds_matrix, columns=df2_cols, index=df1_cols)

    return df_pred


def get_pred_labels(
        table1_df: pd.DataFrame,
        table2_df: pd.DataFrame,
        preds_matrix: pd.DataFrame,
        pred_labels_list: List[NDArray[Any]],
        strategy: Strategy = Strategy.MANY_TO_MANY,
):
    """Get prediction labels based on strategy.

    Args:
        table1_df: Left table DataFrame.
        table2_df: Right table DataFrame.
        preds_matrix: Prediction matrix.
        pred_labels_list: List of prediction labels.
        strategy: Matching strategy.

    Returns:
        pd.DataFrame: Prediction labels matrix.
    """
    # do flatten and get mean
    pred_labels = np.mean(np.array(pred_labels_list), axis=0)

    # TODO: 0.5?
    # (pred_labels > 0.5) ? 1 : 0
    pred_labels = np.where(pred_labels > 0.5, 1, 0)

    # read column names
    df1_cols = table1_df.columns
    df2_cols = table2_df.columns

    # create similarity matrix for pred labels
    # ManyToMany 는 predict 에서 생성된 pred_label 유지
    # OneToMany 는 row 에서 preds 의 최댓값을 취함
    # OneToOne 는 col, row 에서의 최댓값을 취함
    # TODO: move to user select
    if strategy == Strategy.MANY_TO_MANY:
        pred_labels_matrix = np.array(pred_labels).reshape(len(df1_cols), len(df2_cols))
    else:
        pred_labels_matrix = np.zeros((len(df1_cols), len(df2_cols)))

        # pred_labels 가 1인 index 만 순회
        for i, j in np.argwhere(pred_labels == 1):
            max_row = max(preds_matrix[i, :].to_list())
            max_col = max(preds_matrix[:, j].to_list())

            if max_row != preds_matrix[i, j]:
                continue

            if strategy == Strategy.ONE_TO_ONE and preds_matrix[i, j] != max_col:
                continue

            pred_labels_matrix[i, j] = 1

    df_pred_labels = pd.DataFrame(pred_labels_matrix, columns=df2_cols, index=df1_cols)

    return df_pred_labels


def get_predicted_tuples(preds_matrix: pd.DataFrame, pred_labels_matrix: pd.DataFrame) -> List[Tuple[str, str, Scalar]]:
    """Get predicted tuples from prediction matrices.

    Args:
        preds_matrix: Prediction values matrix.
        pred_labels_matrix: Prediction labels matrix.

    Returns:
        List[Tuple[str, str, Scalar]]: List of predicted column matches.
    """
    # tuple l_col_name, r_col_name, predict_value
    predicted_tuples = [
        (str(pred_labels_matrix.index[i]), str(pred_labels_matrix.columns[j]), preds_matrix.iloc[i, j])
        for i, j in zip(*np.where(pred_labels_matrix == 1))
    ]
    return predicted_tuples
