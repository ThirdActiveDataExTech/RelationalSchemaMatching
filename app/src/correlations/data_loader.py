import json
import re
from collections import defaultdict
from typing import Any

import pandas as pd


def read_table(path: str, save_as_csv: bool = False) -> pd.DataFrame:
    """

    Args:
        path: MUST be a path to a csv, json, jsonl file
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
    else:
        raise Exception(f"[Path: {path}] must end with .csv or .json or .jsonl")

    if save_as_csv:
        save_pth = re.sub(r'\.jsonl?', '.csv', path)
        df.to_csv(save_pth, index=False, encoding='utf-8')

    return df


def csv_from_json(json_path: str) -> pd.DataFrame:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    key_values = find_all_keys_values(data, "")

    df = pd.DataFrame({k: pd.Series(v) for k, v in key_values.items()})

    return df


def csv_from_jsonl(jsonl_path: str) -> pd.DataFrame:
    data = [json.loads(line) for line in open(jsonl_path)]

    # need parent key, use TOPLEVEL
    # TODO: replace TOPLEVEL
    key_values = find_all_keys_values({"TOPLEVEL": data}, "TOPLEVEL")

    # remove "TOPLEVEL.", but remains ".*"
    key_values = {k.replace("TOPLEVEL.", ""): v for k, v in key_values.items() if len(v) > 1}

    df = pd.DataFrame({k: pd.Series(v) for k, v in key_values.items()})

    return df


def find_all_keys_values(json_data: Any, parent_key: str) -> defaultdict[Any, list]:
    """
    모든 key, value recursive 하게 순회

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
