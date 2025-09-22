import logging
import os
import uuid
from typing import Optional, Any

from app.src.correlations.data_loader import preprocess_table, check_from_s3, load_from_s3
from app.src.correlations.enums import Strategy, MatchingModel
from app.src.correlations.matching import schema_matching
from app.src.correlations.prediction_analysis import export_metric_as_csv, get_metric

logger = logging.getLogger(__name__)


# TODO: 이름 구체적으로
def run(
        l_table_path: str,
        r_table_path: str,
        truth_json: Optional[str] = None,
        model: MatchingModel = MatchingModel.INITIAL,
        strategy: Strategy = Strategy.MANY_TO_MANY,
        threshold: Optional[float] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region_name: Optional[str] = None,
) -> Any:
    """Run schema matching between two tables.

    Args:
        l_table_path: Path to the left table.
        r_table_path: Path to the right table.
        truth_json: Path to truth JSON file for evaluation.
        model: Matching model to use.
        strategy: Matching strategy.
        threshold: Threshold for matching.
        endpoint_url: S3 endpoint URL.
        access_key: AWS access key.
        secret_key: AWS secret key.
        region_name: AWS region name.

    Returns:
        Any: Matching metrics and results.
    """
    req_id = str(uuid.uuid4())  # TODO: actual uuid
    req_dir = f"tmp/{req_id}"
    os.makedirs(req_dir, exist_ok=True)

    if check_from_s3(l_table_path):
        l_table_path = load_from_s3(l_table_path, req_dir, endpoint_url, access_key, secret_key, region_name)
    l_table = preprocess_table(l_table_path)

    if check_from_s3(r_table_path):
        r_table_path = load_from_s3(r_table_path, req_dir, endpoint_url, access_key, secret_key, region_name)
    r_table = preprocess_table(r_table_path)

    df_pred, df_pred_labels, predicted_tuples = schema_matching(l_table, r_table, model, strategy, threshold)

    export_metric_as_csv(req_dir, df_pred, df_pred_labels)

    metrics = get_metric(predicted_tuples, truth_json, l_table_path, r_table_path)

    return metrics


def match_from_test_dataset(dataset_path: str) -> Any:
    """주어진 데이터셋에서 스키마 매칭을 수행하고 결과를 반환하는 함수.

    Args:
        dataset_path (str):
            - 테이블 파일(Table1.csv, Table2.csv)을 포함하는 데이터셋 경로
            - truth.json 파일이 존재할 경우 F1 Score 계산 가능
            - 파일 형식: CSV만 지원

    Returns:
        Any:
            - 스키마 매칭 예측 결과 (run() 함수의 반환 값)
            - 결과는 result_path에 저장됨
            - truth.json 존재 시 평가 메트릭 포함

    Raises:
        FileNotFoundError:
            - dataset_path가 존재하지 않을 때
            - Table1.csv/Table2.csv 파일이 없을 때
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} does not exist.")

    l_table = os.path.join(dataset_path, "Table1.csv")
    if not os.path.exists(l_table):
        raise FileNotFoundError(f"{l_table} does not exist.")

    r_table = os.path.join(dataset_path, "Table2.csv")
    if not os.path.exists(r_table):
        raise FileNotFoundError(f"{r_table} does not exist.")

    truth_json_path = os.path.join(dataset_path, "truth.json")
    if os.path.exists(truth_json_path):
        truth_json = truth_json_path
    else:
        truth_json = None

    return run(l_table_path=l_table, r_table_path=r_table, truth_json=truth_json)
