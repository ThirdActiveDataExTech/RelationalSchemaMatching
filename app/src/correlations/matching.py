import logging
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb

from app.src.correlations.data_preprocessor import read_table, drop_na_columns
from app.src.correlations.enums import Strategy, MatchingModel
from app.src.correlations.relation_features import create_feature_matrix_inference
from app.src.correlations.util import time_logger


@time_logger
def schema_matching(
        l_table_path: str,
        r_table_path: str,
        model: MatchingModel,
        strategy: Strategy,
        threshold: Optional[float] = None
):
    """

    Args:
        l_table_path: path to l_table
        r_table_path: path to r_table
        model: Schema Matching XGBoost Model
        strategy: matching strategy. Check app.src.correlations.enums.Strategy.
        threshold: correlation value threshold.

    Returns:
        schema matching result
    """

    # read tables.
    l_df = preprocess_table(l_table_path)
    r_df = preprocess_table(r_table_path)

    logging.debug(f"trying to read {r_table_path}")
    r_df = read_table(r_table_path)
    r_df = drop_na_columns(r_df)

    # extract features
    features = create_feature_matrix_inference(l_df, r_df)

    preds, pred_labels_list = predict_inference(features, model, threshold)

    df_pred = postprocess_pred(l_df, r_df, preds)

    # calculate metrics
    df_pred_labels = get_pred_labels(l_df, r_df, df_pred, pred_labels_list, strategy)
    predicted_tuples = get_predicted_tuples(df_pred, df_pred_labels)

    return df_pred, df_pred_labels, predicted_tuples


def preprocess_table(table_path: str) -> pd.DataFrame:
    logging.debug(f"trying to read {table_path}")
    df = read_table(table_path)
    df = drop_na_columns(df)
    return df


def predict_inference(
        features: np.ndarray,
        model: MatchingModel,
        threshold: Optional[float] = None
) -> Tuple[list[np.ndarray], list[np.ndarray]]:
    """
    load model and predict on features
    """
    preds = []
    pred_labels_list = []

    model_files = os.listdir(model.path)
    model_cnt = len(model_files) // 2
    for i in range(model_cnt):
        bst = xgb.Booster({'nthread': 4})  # init model
        model_file = os.path.join(model.path, f"{i}.model")
        bst.load_model(model_file)

        # use specified threshold or model best threshold
        if threshold is not None:
            best_threshold = float(threshold)
        else:
            threshold_file = os.path.join(model.path, f"{i}.threshold")
            with open(threshold_file, "r") as f:
                best_threshold = float(f.read())

        # TODO: UNCHECKED CODE
        labels = np.ones(len(features))
        dtest = xgb.DMatrix(features, label=labels)
        pred = bst.predict(dtest)

        pred_labels = np.where(pred > best_threshold, 1, 0)
        # UNCHECKED CODE

        # Booster 가 결합된 feature 로 predict, 현재 분리 불가
        preds.append(pred)

        pred_labels_list.append(pred_labels)
        del bst

    return preds, pred_labels_list


def postprocess_pred(
        table1_df: pd.DataFrame,
        table2_df: pd.DataFrame,
        preds: list[np.ndarray]
) -> pd.DataFrame:
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
        pred_labels_list: list[np.ndarray],
        strategy: Strategy = Strategy.MANY_TO_MANY
):
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
            max_row = max(preds_matrix[i, :])
            max_col = max(preds_matrix[:, j])

            if max_row != preds_matrix[i, j]:
                continue

            if strategy == Strategy.ONE_TO_ONE and preds_matrix[i, j] != max_col:
                continue

            pred_labels_matrix[i, j] = 1

    df_pred_labels = pd.DataFrame(pred_labels_matrix, columns=df2_cols, index=df1_cols)

    return df_pred_labels


def get_predicted_tuples(
        preds_matrix: pd.DataFrame,
        pred_labels_matrix: pd.DataFrame
) -> list[tuple[str, str, float | int]]:
    # tuple l_col_name, r_col_name, predict_value
    predicted_tuples = [
        (pred_labels_matrix.index[i], pred_labels_matrix.columns[j], preds_matrix.iloc[i, j])
        for i, j in zip(*np.where(pred_labels_matrix == 1))
    ]
    return predicted_tuples
