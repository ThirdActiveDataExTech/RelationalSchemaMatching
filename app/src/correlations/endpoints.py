import json
import logging
import os
from typing import Optional

import pandas as pd
from sklearn.metrics import f1_score

from app.src.correlations.enums import Strategy, MatchingModel
from app.src.correlations.matching import schema_matching
from app.src.correlations.util import time_logger

logger = logging.getLogger(__name__)


def match_from_test_dataset(dataset_path: str) -> any:
    """  
    @param dataset_path: Dataset 경로는 Table1, Table2 두 개의 파일을 가지고 있어야 함.
    Table 파일의 형식은 csv만 지원.
    truth.json 이 있을 경우, F1 Score 계산이 가능함.  
    @return: SchemaMatching Predict result 
    """

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} does not exist.")

    l_table = os.path.join(dataset_path, "Table1.csv")
    if not os.path.exists(l_table):
        raise FileNotFoundError(f"{l_table} does not exist.")

    r_table = os.path.join(dataset_path, "Table1.csv")
    if not os.path.exists(r_table):
        raise FileNotFoundError(f"{r_table} does not exist.")

    result_path = dataset_path

    truth_json = os.path.join(dataset_path, "truth.json")
    if not os.path.exists(truth_json):
        truth_json = None

    return run(l_table, r_table, result_path, truth_json)


# TODO: 이름 구체적으로
@time_logger
def run(
        l_table: str,
        r_table: str,
        result_path: str,
        truth_json: Optional[str] = None,
        model: Optional[MatchingModel] = MatchingModel.INITIAL,
        strategy: Optional[Strategy] = Strategy.MANY_TO_MANY,
        threshold: Optional[float] = None,
        calculate_metrics: bool = True
) -> any:
    df_pred, df_pred_labels, predicted_pairs = schema_matching(l_table, r_table, model, strategy, threshold)

    if result_path and os.path.exists(result_path):
        export_metric_as_csv(result_path, df_pred, df_pred_labels)

    if calculate_metrics:
        get_metric(predicted_pairs, truth_json)

    return True


def export_metric_as_csv(result_path: str, df_pred: pd.DataFrame, df_pred_labels: pd.DataFrame):
    pred_path = os.path.join(result_path, "similarity_matrix_value.csv")
    df_pred.to_csv(pred_path, index=True)
    logging.info(f"value.csv saved to {pred_path}")

    pred_label_path = os.path.join(result_path, "similarity_matrix_label.csv")
    df_pred_labels.to_csv(pred_label_path, index=True)
    logging.info(f"label.csv saved to {pred_label_path}")


# TODO: specify type predicted_pairs 
def get_metric(predicted_pairs: list[tuple[str, str, any]], truth_json: Optional[str] = None):
    # 스키마 매칭 결과 log 출력
    logging.info("Predicted Pairs:")
    for pair in predicted_pairs:
        logging.info(pair)

    if truth_json and os.path.exists(truth_json):
        with open(truth_json) as f:
            json_data = json.load(f)
        y_true = [(m['source_column'], m['target_column']) for m in json_data['matches']]
        y_pred = [(pt[0], pt[1]) for pt in predicted_pairs]

        # y_true와 y_pred의 고유한 쌍을 설정
        unique_labels = set(y_true) | set(y_pred)

        # y_true와 y_pred를 이진 벡터로 변환
        y_true_binary = [1 if label in y_true else 0 for label in unique_labels]
        y_pred_binary = [1 if label in y_pred else 0 for label in unique_labels]

        logging.info(f"F1 Score: {f1_score(y_true_binary, y_pred_binary, average='binary')}")
