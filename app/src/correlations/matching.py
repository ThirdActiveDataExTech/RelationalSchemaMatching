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

    # filter columns
    logging.debug(f"trying to read {l_table_path}")
    l_df = read_table(l_table_path)
    l_df = drop_na_columns(l_df)

    logging.debug(f"trying to read {r_table_path}")
    r_df = read_table(r_table_path)
    r_df = drop_na_columns(r_df)

    # extract features
    features = create_feature_matrix_inference(l_df, r_df)

    preds, pred_labels_list = predict_inference(features, model, threshold)

    # MAYBE METRIC
    df_pred, df_pred_labels, predicted_pairs = create_similarity_matrix(l_df, r_df, preds, pred_labels_list,
                                                                        strategy=strategy)
    return df_pred, df_pred_labels, predicted_pairs


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


def create_similarity_matrix(
        table1_df: pd.DataFrame,
        table2_df: pd.DataFrame,
        preds: list[np.ndarray],
        pred_labels_list: list[np.ndarray],
        strategy: Strategy = Strategy.MANY_TO_MANY
):
    """
    Create a similarity matrix from the prediction
    """

    predicted_pairs = []
    preds = np.array(preds)
    preds = np.mean(preds, axis=0)
    pred_labels_list = np.array(pred_labels_list)
    pred_labels = np.mean(pred_labels_list, axis=0)
    pred_labels = np.where(pred_labels > 0.5, 1, 0)

    # read column names
    df1_cols = table1_df.columns
    df2_cols = table2_df.columns

    # create similarity matrix for pred values
    preds_matrix = np.array(preds).reshape(len(df1_cols), len(df2_cols))

    # create similarity matrix for pred labels
    # ManyToMany 와 타 strategy가 동일한 로직을 사용 하는 것으로 보임
    if strategy == Strategy.MANY_TO_MANY:
        pred_labels_matrix = np.array(pred_labels).reshape(len(df1_cols), len(df2_cols))
    else:
        pred_labels_matrix = np.zeros((len(df1_cols), len(df2_cols)))
        for i in range(len(df1_cols)):
            for j in range(len(df2_cols)):
                if pred_labels[i * len(df2_cols) + j] != 1:
                    continue

                max_row = max(preds_matrix[i, :])
                if max_row != preds_matrix[i, j]:
                    continue

                if strategy == Strategy.ONE_TO_ONE:
                    max_col = max(preds_matrix[:, j])
                    if preds_matrix[i, j] != max_col:
                        continue

                pred_labels_matrix[i, j] = 1

    df_pred = pd.DataFrame(preds_matrix, columns=df2_cols, index=df1_cols)
    df_pred_labels = pd.DataFrame(pred_labels_matrix, columns=df2_cols, index=df1_cols)
    for i in range(len(df_pred_labels)):
        for j in range(len(df_pred_labels.iloc[i])):
            if df_pred_labels.iloc[i, j] == 1:
                predicted_pairs.append((df_pred.index[i], df_pred.columns[j], df_pred.iloc[i, j]))

    return df_pred, df_pred_labels, predicted_pairs
