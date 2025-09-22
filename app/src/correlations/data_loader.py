import json
import logging
import os
import re
from collections import defaultdict
from typing import Any, Optional
from urllib.parse import urlparse

import pandas as pd

from app.src.correlations.data_cleaner import drop_na_columns
from app.src.fetcher.s3 import S3Connector


def read_table(path: str, save_as_csv: bool = False) -> pd.DataFrame:
    """Read table from various file formats.

    Args:
        path: MUST be a path to a csv, json, jsonl, parquet file
        save_as_csv: save the table as a csv file
    Return:
        pd.DataFrame
    """
    df: pd.DataFrame
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        df = csv_from_json(path)
    elif path.endswith(".jsonl"):
        df = csv_from_jsonl(path)
    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        raise Exception(f"[Path: {path}] must end with .csv or .json or .jsonl or .parquet")

    if save_as_csv:
        save_pth = re.sub(r'\.jsonl?', '.csv', path)
        df.to_csv(save_pth, index=False, encoding='utf-8')

    return df


def csv_from_json(json_path: str) -> pd.DataFrame:
    """Convert JSON file to DataFrame.

    Args:
        json_path: Path to JSON file.

    Returns:
        pd.DataFrame: Converted DataFrame.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    key_values = find_all_keys_values(data, "")

    df = pd.DataFrame({k: pd.Series(v) for k, v in key_values.items()})

    return df


def csv_from_jsonl(jsonl_path: str) -> pd.DataFrame:
    """Convert JSONL file to DataFrame.

    Args:
        jsonl_path: Path to JSONL file.

    Returns:
        pd.DataFrame: Converted DataFrame.
    """
    data = [json.loads(line) for line in open(jsonl_path)]

    # need parent key, use TOPLEVEL
    # TODO: replace TOPLEVEL
    key_values = find_all_keys_values({"TOPLEVEL": data}, "TOPLEVEL")

    # remove "TOPLEVEL.", but remains ".*"
    clean_kvs = {k.replace("TOPLEVEL.", ""): v for k, v in key_values.items() if len(v) > 1}

    df = pd.DataFrame({k: pd.Series(v) for k, v in clean_kvs.items()})

    return df


def find_all_keys_values(json_data: Any, parent_key: str) -> defaultdict[Any, list]:
    """모든 key, value recursive 하게 순회

    Find all keys that don't have list or dictionary values and their values.
    Key should be saved with its parent key like "parent-key.key".
    """
    key_values = defaultdict(list)
    for key, value in json_data.items():
        full_key = f"{parent_key}.{key}"
        if isinstance(value, dict):
            value = [value]

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    child_key_values = find_all_keys_values(item, key)
                    for child_key, child_value in child_key_values.items():
                        key_values[child_key].extend(child_value)
                else:
                    key_values[full_key].append(item)
        else:
            key_values[full_key].append(value)

    return key_values


def check_from_s3(data_path: str) -> bool:
    """Check if the path is a valid S3 URI.

    Args:
        data_path: Path to check.

    Returns:
        bool: True if valid S3 URI, False otherwise.
    """
    # 경로 검증 정규식 (AWS S3 명명 규칙 반영)
    s3_path_regex = r"^s3://(?P<bucket>[a-z0-9.-]{3,63})/(?P<key>.+)$"

    return False if re.match(s3_path_regex, data_path) is None else True


def load_from_s3(s3_uri: str, req_path: str, endpoint_url: Optional[str] = None, access_key: Optional[str] = None,
                 secret_key: Optional[str] = None, region_name: Optional[str] = None):
    """Download file from S3 to local path.

    Args:
        s3_uri: S3 URI of the file.
        req_path: Local directory to save the file.
        endpoint_url: S3 endpoint URL.
        access_key: AWS access key.
        secret_key: AWS secret key.
        region_name: AWS region name.

    Returns:
        str: Local file path.
    """
    parsed = urlparse(s3_uri)

    bucket_name = parsed.netloc
    object_key = parsed.path.lstrip("/")

    local_file = os.path.basename(object_key)
    local_path = os.path.join(req_path, local_file)

    try:
        s3_connector = S3Connector(endpoint_url=endpoint_url, access_key=access_key, secret_key=secret_key,
                                   region_name=region_name)

        if not s3_connector.download_file(bucket_name=bucket_name, object_name=object_key, file_path=local_path):
            raise Exception("l_table download failed")

        return local_path
    except Exception as e:
        raise Exception(f"{__name__}: `{s3_uri=}` download failed, {e=}")


def preprocess_table(table_path: str) -> pd.DataFrame:
    """Preprocess table by reading and cleaning.

    Args:
        table_path: Path to the table file.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    logging.debug(f"trying to read {table_path}")
    df = read_table(table_path)
    df = drop_na_columns(df)
    return df
