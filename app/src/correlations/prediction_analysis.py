import json
import logging
import os
from typing import List, Any, Optional, Dict, Tuple

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score


def export_metric_as_csv(result_path: str, df_pred: pd.DataFrame, df_pred_labels: pd.DataFrame):
    """Export prediction metrics as CSV files.

    Args:
        result_path: Directory path to save CSV files.
        df_pred: Prediction values DataFrame.
        df_pred_labels: Prediction labels DataFrame.
    """
    pred_path = os.path.join(result_path, "similarity_matrix_value.csv")
    df_pred.to_csv(pred_path, index=True)
    logging.info(f"value.csv saved to {pred_path}")

    pred_label_path = os.path.join(result_path, "similarity_matrix_label.csv")
    df_pred_labels.to_csv(pred_label_path, index=True)
    logging.info(f"label.csv saved to {pred_label_path}")


def calculate_evaluation_metrics(predicted_tuples: List[Tuple[str, str, Any]], truth_json: str) -> Tuple[List[Tuple[str, str]], Dict[str, Any]]:
    """Calculate evaluation metrics from ground truth.

    Args:
        predicted_tuples: List of predicted column matches.
        truth_json: Path to ground truth JSON file.

    Returns:
        Tuple[List[Tuple[str, str]], Dict[str, Any]]: True pairs and evaluation metrics.
    """
    with open(truth_json) as f:
        json_data = json.load(f)

    y_true = [(m['source_column'], m['target_column']) for m in json_data['matches']]
    y_pred = [(pt[0], pt[1]) for pt in predicted_tuples]

    unique_labels = set(y_true) | set(y_pred)

    y_true_binary = [1 if label in y_true else 0 for label in unique_labels]
    y_pred_binary = [1 if label in y_pred else 0 for label in unique_labels]

    evaluation_metrics = {
        "precision": float(precision_score(y_true_binary, y_pred_binary, average='binary')),
        "recall": float(recall_score(y_true_binary, y_pred_binary, average='binary')),
        "f1": float(f1_score(y_true_binary, y_pred_binary, average='binary')),
        "total_pairs": len(unique_labels),
        "true_positive_count": sum(1 for p in y_pred if p in y_true),
        "false_positive_count": sum(1 for p in y_pred if p not in y_true)
    }

    return y_true, evaluation_metrics
