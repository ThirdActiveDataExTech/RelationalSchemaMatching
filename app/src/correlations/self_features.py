import logging
import random
import re
from enum import Enum

import numpy as np
import pandas as pd
from dateutil.parser import parse as parse_date

from app.src.correlations.model import SentenceTransformer

"""
한자 번체, 신자체, 영어 dataset에서 숫자 단위를 변환하기 위한 dict
"""
UNIT_DICT = {"万": 10000, "亿": 100000000, "萬": 10000, "億": 100000000, "K+": 1000, "M+": 1000000, "B+": 1000000000}

DATE_DICT = {"月", "日", "年"}
PUNCTUATIONS = [",", ".", ";", "!", "?", "，", "。", "；", "！", "？"]
SPECIAL_CHARACTERS = ["／", "/", "\\", "-", "_", "+", "=", "*", "&", "^", "%", "$", "#", "@", "~", "`", "(", ")",
                      "[", "]", "{", "}", "<", ">", "|", "'", "\""]


class DataTypes(Enum):
    URL = 0,
    MAINLY_NUMERIC = 1,
    DATE = 2,
    STRING = 3,
    # TODO: replace 1
    STRICT_NUMERIC = 1

    def __len__(self):
        return len(self.__class__.__members__)


class Constants:
    DATE_RATIO = 0.9
    URL_RATIO = 0.9
    NUMERIC_PART_RATIO = 0.5
    STRICT_NUMERIC_RATIO = 0.95
    MAINLY_NUMERIC_RATIO = 0.9

    NUMERIC_FEATURES_DIMENSION = 6
    CHARACTER_FEATURES_DIMENSION = 8
    DEEP_EMBEDDING_FEATURES_DIMENSION = 768

    # features 에서 -1과 -999는 유효하지 않은 값을 나타내는 것으로 보임
    GENERAL_FEATURE_INVALID_VALUE = -1
    DEEP_FEATURE_INVALID_VALUE = -999


def make_self_features_from(table_df: pd.DataFrame) -> np.ndarray:
    """

    Returns:
         np.ndarray: Extracts features from the given table path and returns a feature table.
    """
    feature_array = []
    for column in table_df.columns:
        # TODO: why use "Unnamed:"
        if "Unnamed:" in column:
            continue

        feature = extract_features(table_df[column]).reshape(1, -1)
        feature_array.append(feature)

    if len(feature_array) == 0:
        raise ValueError(f"No features extracted. Check your table: {table_df}.")

    # get each columns features and concatenate all features
    # will make (columns_length, feature_matrix_len)
    # should be (len(columns), 792)
    features = np.vstack(feature_array)

    logging.debug(f"make_self_features_from(): {features.shape}")

    return features


# REMINDER: use ONLY data_list as Column
def extract_features(data_list: list[any]) -> np.ndarray:
    """

    Args:
        data_list (list[any]): data can be column or list.
    Returns:
        np.array: Extract features from the given data.
    """

    # Drop outlier columns
    data_list = [d for d in data_list if d == d and d != "--"]

    data_type = classify_data_type(data_list)

    # TODO: ignored comment, need to fix this
    # If data is not numeric, give length features
    length_features = calculate_numeric_features([len(str(d)) for d in data_list])

    # output_features
    output_features = np.concatenate((
        get_datatype_feature(data_type),  # 4 cols
        get_data_numeric_feature(data_list, data_type),  # 6 cols
        length_features,  # 6 cols
        get_character_feature(data_list, data_type),  # 8 cols
        get_deep_embedding_feature(data_list, data_type)  # 768 cols
    ))

    return output_features


def classify_data_type(data_list: list[any]) -> DataTypes:
    data_type = DataTypes.STRING
    if is_url(data_list):
        data_type = DataTypes.URL
    elif is_date(data_list):
        data_type = DataTypes.DATE
    elif is_strict_numeric(data_list):
        data_type = DataTypes.STRICT_NUMERIC
    elif is_mainly_numeric(data_list):
        data_type = DataTypes.MAINLY_NUMERIC

    return data_type


def is_url(data_list: list[any]) -> bool:
    """

    Returns:
        bool: True if data_list contains url strings than URL_RATIO
    """
    cnt = 0
    url_pattern = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    for data in data_list:
        if not isinstance(data, str):
            continue
        if re.search(url_pattern, data):
            cnt += 1

    return cnt >= Constants.URL_RATIO * len(data_list)


def is_date(data_list: list[any]) -> bool:
    """

    Returns:
        bool: True if data_list contains date strings than DATE_RATIO
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
            # TODO: 왜 2000 년 전, 2030 년 이후 데이터 drop?
            if date.year < 2000 or date.year > 2030:
                continue
            cnt += 1
        except Exception as _:
            continue

    return cnt >= Constants.DATE_RATIO * len(data_list)


def is_strict_numeric(data_list: list[any], verbose: bool = False) -> bool:
    """

    Args:
        data_list: 확인할 데이터
        verbose: for debugging

    Returns: 
        bool: data_list 내의 numeric 비율이 STRICT_NUMERIC_RATIO 이상일 경우 True

    """
    cnt = 0
    for x in data_list:
        try:
            y = float(x)
            if verbose:
                logging.debug(f"is_strict_numeric: src:{x} float{y}")
            cnt += 1
        except ValueError as _:
            continue

    return cnt >= Constants.STRICT_NUMERIC_RATIO * len(data_list)


def is_mainly_numeric(data_list: list[any]) -> bool:
    """data 내 numeric part 가 정해진 비율 이상일 경우 mainly_numeric 으로 판단함

    Returns:
        bool: data_list 내의 mainly_numeric 비율이 STRICT_NUMERIC_RATIO 이상일 경우 True

    """
    cnt = 0
    for data in data_list:
        data = str(data)
        data = data.replace(",", "")

        # 백, 천, 만, K, B등의 단위 제거
        for unit in UNIT_DICT.keys():
            data = data.replace(unit, "")

        # data 내 numeric part 가 NUMERIC_PART_RATIO 이상일 경우 True
        numeric_part = re.findall(r'\d+', data)
        if len(numeric_part) > 0 and sum(len(x) for x in numeric_part) >= Constants.NUMERIC_PART_RATIO * len(data):
            cnt += 1

    return cnt >= Constants.MAINLY_NUMERIC_RATIO * len(data_list)


def extract_numeric(data_list: list[any]) -> list[float]:
    """

    Notes:
        unit 간 우선순위가 존재하지 않아, "3亿5万" 같은 케이스에서 亿 대신 万가 사용되어 원본 값과 크게 차이 날 수 있음.
        unit 이 존재한다면 이후의 값이 유실됨, "3万5"의 경우 30000.0 으로 변환됨.
        한글에서 "1억 5천만"과 같이 숫자 내 whitespace를 사용하는 경우 drop 됨.
        "만", "亿" 과 같은 unit 사용된 문자열의 경우 drop 됨.

    Args:
        data_list: DataType.NUMERIC 이 검증된 데이터

    Returns:
        list[float]: Extracts numeric part(including float) from string list

    """
    try:
        data_list = [float(d) for d in data_list]
    except ValueError as _:
        logging.warning(f"{__name__}: data_list can not conversion to float list")
        pass

    numeric_list = []
    for data in data_list:
        data = str(data)
        data = data.replace(",", "")

        # find all numeric parts as [list[tuple[str, str]]
        # TODO: use only first index value, replace re.findall()
        matched = re.findall(r'(-?(\d*[.])?\d+)', data)

        if len(matched) <= 0:
            logging.warning(f"{__name__}: data does not contain any numeric part.")
            continue

        # use first part only
        float_part = float(matched[0][0])

        # unit_key에 해당하는 부분이 있다면, 숫자로 변환
        # TODO: unit priority
        unit = 1
        for unit_key in UNIT_DICT.keys():
            if unit_key in data:
                unit = UNIT_DICT[unit_key]
                break

        numeric_list.append(float_part * unit)

    return numeric_list


def calculate_numeric_features(data_list: list[any]) -> np.array:
    """

    Returns:
        np.array: Extracts numeric features from the given data.

        Including Mean, Min, Max, Variance, Standard Deviation, and the number of unique values.
    """
    mean = np.mean(data_list)
    min = np.min(data_list)
    max = np.max(data_list)
    variance = np.var(data_list)
    cv = np.var(data_list) / mean
    unique = len(set(data_list))
    return np.array([mean, min, max, variance, cv, unique / len(data_list)])


def calculate_character_features(data_list: list[any]) -> np.array:
    """

    Returns:
         np.array: Extracts character features from the given data.
    """
    whitespace_ratios = []  # Ratio of whitespace to length
    punctuation_ratios = []  # Ratio of punctuation to length
    special_character_ratios = []  # Ratio of special characters to length
    numeric_ratios = []  # Ratio of numeric to length

    for data in data_list:
        # data 의 각 문자 x가 자기 문자일 경우 count 1 증가
        whitespace_ratio = (data.count(" ") + data.count("\t") + data.count("\n")) / len(data)
        whitespace_ratios.append(whitespace_ratio)

        punctuation_ratio = sum(1 for x in data if x in PUNCTUATIONS) / len(data)
        punctuation_ratios.append(punctuation_ratio)

        special_character_ratio = sum(1 for x in data if x in SPECIAL_CHARACTERS) / len(data)
        special_character_ratios.append(special_character_ratio)

        numeric_ratio = sum(1 for x in data if x.isdigit()) / len(data)
        numeric_ratios.append(numeric_ratio)

    # TODO: why use 1e-12
    epsilon = np.array([1e-12] * len(data_list))

    whitespace_ratios = np.array(whitespace_ratios + epsilon)
    punctuation_ratios = np.array(punctuation_ratios + epsilon)
    special_character_ratios = np.array(special_character_ratios + epsilon)
    numeric_ratios = np.array(numeric_ratios + epsilon)

    return np.array([
        # Means
        np.mean(whitespace_ratios),
        np.mean(punctuation_ratios),
        np.mean(special_character_ratios),
        np.mean(numeric_ratios),
        # CVs
        np.var(whitespace_ratios) / np.mean(whitespace_ratios),
        np.var(punctuation_ratios) / np.mean(punctuation_ratios),
        np.var(special_character_ratios) / np.mean(special_character_ratios),
        np.var(numeric_ratios) / np.mean(numeric_ratios)
    ])


def deep_embedding(data_list: list[any]) -> np.ndarray:
    """

    Notes:
        Deep Embedding Feature 는 data 를 SentenceTransformer 로 encoding 후 값들의 mean 을 취함.
        20 개의 데이터를 Sampling 하여 사용.

    Returns:
        np.ndarray: Extracts deep embedding features from the given data using sentence-transformers.
    """
    # TODO: 20개 이외의 값, 20개 미만일 떄 dimension 유지되는지?
    if len(data_list) >= 20:
        data_list = random.sample(data_list, 20)  # safe random checked

    # TODO: use Depends
    model = SentenceTransformer.get()

    # str encode
    # TODO: check side effect
    embeddings = np.array(model.encode(data_list))

    return np.mean(embeddings, axis=0)


def get_datatype_feature(data_type: DataTypes) -> np.ndarray:
    """

    Returns:  Make data type feature one hot encoding
    """

    # TODO: rely on enum len. when datatypes changes make XGBoost Length err.
    data_type_feature = np.zeros(len(DataTypes) - 1)
    data_type_feature[data_type.value] = 1

    return data_type_feature


def get_data_numeric_feature(data_list: list[any], data_type: DataTypes) -> np.ndarray:
    """

    Returns:
        np.ndarray: Get numeric features if the data MAINLY_NUMERIC or STRICT_NUMERIC, else invalid values matrix.
    """

    if data_type == DataTypes.MAINLY_NUMERIC or data_type == DataTypes.STRICT_NUMERIC:
        data_numeric = extract_numeric(data_list)
        numeric_features = calculate_numeric_features(data_numeric)
    else:
        # dont use numeric features, give default  invalid values
        numeric_features = np.array([Constants.GENERAL_FEATURE_INVALID_VALUE] * Constants.NUMERIC_FEATURES_DIMENSION)

    return numeric_features


def get_character_feature(data_list: list[any], data_type: DataTypes) -> np.ndarray:
    """

    Returns:
        np.ndarray: Give character features if the data is STRING or MAINLY_NUMERIC, else invalid values matrix.
    """
    if data_type == DataTypes.STRING or data_type == DataTypes.MAINLY_NUMERIC:
        character_feature = calculate_character_features(data_list)
    else:
        character_feature = np.array([Constants.GENERAL_FEATURE_INVALID_VALUE] * Constants.CHARACTER_FEATURES_DIMENSION)

    return character_feature


def get_deep_embedding_feature(data_list: list[any], data_type: DataTypes) -> np.ndarray:
    """

    Returns:
        np.ndarray: Give deep embeddings if the data is STRING or MAINLY_NUMERIC, else invalid values matrix.
    """

    if data_type == DataTypes.STRING or data_type == DataTypes.MAINLY_NUMERIC:
        deep_embedding_feature = deep_embedding(data_list)
    else:
        deep_embedding_feature = np.array([Constants.DEEP_FEATURE_INVALID_VALUE]
                                          * Constants.DEEP_EMBEDDING_FEATURES_DIMENSION)

    return deep_embedding_feature
