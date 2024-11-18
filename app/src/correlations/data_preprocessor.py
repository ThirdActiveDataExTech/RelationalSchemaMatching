import json
import logging
import re
from collections import defaultdict

import pandas as pd


def read_table(path: str) -> pd:
    """
    Params: path MUST be a path to a csv, json, jsonl file
    Returns: pandas dataframe
    """
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json") or path.endswith(".jsonl"):
        df = csv_from_json(path)
    else:
        raise Exception(f"[Path: {path}] must end with .csv or .json or .jsonl")
    return df


def csv_from_json(path: str) -> pd.DataFrame:
    if path.endswith(".json"):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif path.endswith(".jsonl"):
        data = [json.loads(line) for line in open(path)]
    else:
        raise Exception(f"[Path: {path}] must end with .json or .jsonl")

    # find key_values
    if isinstance(data, dict):
        key_values = find_all_keys_values(data, "")
    elif isinstance(data, list):
        key_values = find_all_keys_values({"TOPLEVEL": data}, "TOPLEVEL")
    else:
        raise ValueError(f"Path: {path} is not a dictionary or list")

    key_values = {k.replace("TOPLEVEL.", ""): v for k, v in key_values.items() if len(v) > 1}

    df = pd.DataFrame({k: pd.Series(v) for k, v in key_values.items()})
    # save to csv
    save_pth = re.sub(r'\.jsonl?', '.csv', path)
    df.to_csv(save_pth, index=False, encoding='utf-8')
    return df


def find_all_keys_values(json_data: any, parent_key: str) -> defaultdict[any, list]:
    """
    Find all keys that don't have list or dictionary values and their values. 
    Key should be saved with its parent key like "parent-key.key".
    """
    key_values = defaultdict(list)
    for key, value in json_data.items():
        if isinstance(value, dict):
            child_key_values = find_all_keys_values(value, key)
            for child_key, child_value in child_key_values.items():
                key_values[child_key].extend(child_value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    child_key_values = find_all_keys_values(item, key)
                    for child_key, child_value in child_key_values.items():
                        key_values[child_key].extend(child_value)
                else:
                    key_values[parent_key + "." + key].append(item)
        else:
            key_values[parent_key + "." + key].append(value)
    return key_values


def drop_na_columns(table_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that have zero instances or all columns are "--"
    """
    original_columns = table_df.columns
    for column in table_df.columns:
        column_data = [d for d in list(table_df[column]) if d == d and d != "--"]
        if len(column_data) <= 1:
            table_df = table_df.drop(column, axis=1)
            continue
        if "Unnamed:" in column:
            table_df = table_df.drop(column, axis=1)
            continue
    remove_columns = list(set(original_columns) - set(table_df.columns))
    if len(remove_columns) > 0:
        logging.info(f"Removed columns: {remove_columns}")
    return table_df
