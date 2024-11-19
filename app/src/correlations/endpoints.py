import json
import logging
import os
from typing import Optional

from sklearn.metrics import f1_score

from app.src.correlations.enums import Strategy, MatchingModel
from app.src.correlations.matching import schema_matching
from app.src.correlations.util import time_logger


@time_logger
def run(
        l_table: str,
        r_table: str,
        result_path: str,
        truth_json: Optional[str] = None,
        model: Optional[MatchingModel] = MatchingModel.INITIAL,
        strategy: Optional[Strategy] = Strategy.MANY_TO_MANY,
        threshold: Optional[float] = None
) -> any:
    df_pred, df_pred_labels, predicted_pairs = schema_matching(l_table, r_table, model, strategy, threshold)

    pred_path = os.path.join(result_path, "similarity_matrix_value.csv")
    df_pred.to_csv(pred_path, index=True)

    pred_label_path = os.path.join(result_path, "similarity_matrix_label.csv")
    df_pred_labels.to_csv(pred_label_path, index=True)

    if truth_json is not None and os.path.exists(truth_json):
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

    logging.info("Predicted Pairs:")
    for pair in predicted_pairs:
        logging.info(pair)

    return True
