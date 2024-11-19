import logging
import random
import re
from enum import Enum

import numpy as np
import pandas as pd
from dateutil.parser import parse as parse_date

from app.src.correlations.model import SentenceTransformer

# 중국어 dataset에서 숫자 단위를 변환하기 위한 Dictionary
UNIT_DICT = {"万": 10000, "亿": 100000000, "萬": 10000, "億": 100000000, "K+": 1000, "M+": 1000000, "B+": 1000000000}
DATE_DICT = {"月", "日", "年"}
PUNCTUATIONS = [",", ".", ";", "!", "?", "，", "。", "；", "！", "？"]
SPECIAL_CHARACTERS = ["／", "/", "\\", "-", "_", "+", "=", "*", "&", "^", "%", "$", "#", "@", "~", "`", "(", ")",
                      "[", "]", "{", "}", "<", ">", "|", "'", "\""]


class DataTypes(Enum):
    URL = 0,
    NUMERIC = 1,
    DATE = 2,
    STRING = 3

    def __len__(self):
        return len(self.__class__.__members__)


def is_strict_numeric(data_list: list[any], verbose: bool = False) -> bool:
    """
    @param verbose: for debugging
    @return if data_list contains only numeric values True
    """
    cnt = 0
    for x in data_list:
        try:
            y = float(x)
            if verbose:
                print(x)
                print(y)
            cnt += 1
        except ValueError as _:
            continue
    if cnt >= 0.95 * len(data_list):
        return True

    return False


def is_mainly_numeric(data_list: list[any]) -> bool:
    """
    @return if data_list contains mostly numeric values True
    """
    cnt = 0
    for data in data_list:
        data = str(data)
        data = data.replace(",", "")
        for unit in UNIT_DICT.keys():
            data = data.replace(unit, "")
        numeric_part = re.findall(r'\d+', data)
        if len(numeric_part) > 0 and sum(len(x) for x in numeric_part) >= 0.5 * len(data):
            cnt += 1

    if cnt >= 0.9 * len(data_list):
        return True

    return False


def extract_numeric(data_list: list[any]) -> list[float]:
    """
    @return Extracts numeric part(including float) from string list
    """
    try:
        data_list = [float(d) for d in data_list]
    except ValueError as _:
        pass
    numeric_part = []
    unit = []
    for data in data_list:
        data = str(data)
        data = data.replace(",", "")
        numeric_part.append(re.findall(r'([-]?([0-9]*[.])?[0-9]+)', data))

        # unit_key에 해당하는 부분이 있다면, 숫자로 변환
        this_unit = 1
        for unit_key in UNIT_DICT.keys():
            if unit_key in data:
                this_unit = UNIT_DICT[unit_key]
                break
        unit.append(this_unit)

    numeric_part = [x for x in numeric_part if len(x) > 0]
    if len(numeric_part) != len(data_list):
        logging.warning(
            f"Warning: extract_numeric() found different number of numeric part({len(numeric_part)}) and data list({len(data_list)})")
    numeric_part = [float(x[0][0]) * unit[i] for i, x in enumerate(numeric_part)]
    return numeric_part


def numeric_features(data_list: list[any]) -> np.array:
    """
    @return Extracts numeric features from the given data. Including Mean,Min, Max, Variance, Standard Deviation, and the number of unique values.
    """
    mean = np.mean(data_list)
    min = np.min(data_list)
    max = np.max(data_list)
    variance = np.var(data_list)
    cv = np.var(data_list) / mean
    unique = len(set(data_list))
    return np.array([mean, min, max, variance, cv, unique / len(data_list)])


def is_url(data_list: list[any]) -> bool:
    """
    @return True if data_list contains url strings
    """
    cnt = 0
    url_pattern = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    for data in data_list:
        if not isinstance(data, str):
            continue
        if re.search(url_pattern, data):
            cnt += 1
    if cnt >= 0.9 * len(data_list):
        return True

    return False


def is_date(data_list: list[any]) -> bool:
    """
    @return True if data_list contains date format strings.
    """
    cnt = 0
    for data in data_list:
        if not isinstance(data, str):
            continue

        if any(date in data for date in DATE_DICT):
            cnt += 1

        try:
            date = parse_date(data)
            # check if the date is near to today
            if date.year < 2000 or date.year > 2030:
                continue
            cnt += 1
        except Exception as _:
            continue

    if cnt >= 0.9 * len(data_list):
        return True
    return False


def character_features(data_list: list[any]) -> np.array:
    """
    @return Extracts character features from the given data
    """
    whitespace_ratios = []  # Ratio of whitespace to length
    punctuation_ratios = []  # Ratio of punctuation to length
    special_character_ratios = []  # Ratio of special characters to length
    numeric_ratios = []  # Ratio of numeric to length

    for data in data_list:
        # data 의 각 문자 x가 자기 문자일 경우 1을 더함
        whitespace_ratio = (data.count(" ") + data.count("\t") + data.count("\n")) / len(data)
        whitespace_ratios.append(whitespace_ratio)

        punctuation_ratio = sum(1 for x in data if x in PUNCTUATIONS) / len(data)
        punctuation_ratios.append(punctuation_ratio)

        special_character_ratio = sum(1 for x in data if x in SPECIAL_CHARACTERS) / len(data)
        special_character_ratios.append(special_character_ratio)

        numeric_ratio = sum(1 for x in data if x.isdigit()) / len(data)
        numeric_ratios.append(numeric_ratio)

    epsilon = np.array([1e-12] * len(data_list))
    whitespace_ratios = np.array(whitespace_ratios + epsilon)
    punctuation_ratios = np.array(punctuation_ratios + epsilon)
    special_character_ratios = np.array(special_character_ratios + epsilon)
    numeric_ratios = np.array(numeric_ratios + epsilon)
    return np.array([
        np.mean(whitespace_ratios),
        np.mean(punctuation_ratios),
        np.mean(special_character_ratios),
        np.mean(numeric_ratios),
        np.var(whitespace_ratios) / np.mean(whitespace_ratios),
        np.var(punctuation_ratios) / np.mean(punctuation_ratios),
        np.var(special_character_ratios) / np.mean(special_character_ratios),
        np.var(numeric_ratios) / np.mean(numeric_ratios)
    ])


def deep_embedding(data_list: list[any]) -> any:
    """
    @return Extracts deep embedding features from the given data using sentence-transformers.
    """
    if len(data_list) >= 20:
        data_list = random.sample(data_list, 20)
    model = SentenceTransformer.get()
    embeddings = [model.encode(str(data)) for data in data_list]
    embeddings = np.array(embeddings)
    return np.mean(embeddings, axis=0)


def extract_features(data_list: list[any]) -> np.ndarray:
    """
    @return Extract some features from the given data(column) or list
    """

    # Drop outlier columns.
    data_list = [d for d in data_list if d == d and d != "--"]

    # Classify the data's type, URL or Date or Numeric
    data_type = DataTypes.STRING
    if is_url(data_list):
        data_type = DataTypes.URL
    elif is_date(data_list):
        data_type = DataTypes.DATE
    elif is_strict_numeric(data_list) or is_mainly_numeric(data_list):
        data_type = DataTypes.NUMERIC

    # Make data type feature one hot encoding
    data_type_feature = np.zeros(len(DataTypes))
    data_type_feature[data_type.value] = 1

    # Give numeric features if the data is mostly numeric
    if data_type == DataTypes.NUMERIC:
        data_numeric = extract_numeric(data_list)
        num_fts = numeric_features(data_numeric)
    else:
        num_fts = np.array([-1] * 6)

    # If data is not numeric, give length features
    length_fts = numeric_features([len(str(d)) for d in data_list])

    # Give character features and deep embeddings if the data is string
    if data_type == DataTypes.STRING or (not is_strict_numeric(data_list) and is_mainly_numeric(data_list)):
        char_fts = character_features(data_list)
        deep_fts = deep_embedding(data_list)
    else:
        char_fts = np.array([-1] * 8)
        deep_fts = np.array([-999] * 768)

    output_features = np.concatenate((data_type_feature, num_fts, length_fts, char_fts, deep_fts))
    return output_features


def make_self_features_from(table_df: pd.DataFrame) -> np.ndarray:
    """
    @type table_df: pd.DataFrame
    @return Extracts features from the given table path and returns a feature table.
    """
    feature_array = []
    for column in table_df.columns:
        if "Unnamed:" in column:
            continue
        feature = extract_features(table_df[column]).reshape(1, -1)
        feature_array.append(feature)

    features = np.vstack(feature_array) if feature_array else None
    logging.debug(f"make_self_features_from(): {features.shape}\n{features}")

    return features
