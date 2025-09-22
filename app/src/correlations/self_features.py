import logging
import random
import re
from typing import Any, List, Tuple, Dict

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from app.src.correlations.constants import constants
from app.src.correlations.data_classifier import DataTypes, classify_data_type
from app.src.correlations.model import SentenceTransformer

PUNCTUATIONS = [",", ".", ";", "!", "?", "，", "。", "；", "！", "？"]
SPECIAL_CHARACTERS = ["／", "/", "\\", "-", "_", "+", "=", "*", "&", "^", "%", "$", "#", "@", "~", "`", "(", ")",
                      "[", "]", "{", "}", "<", ">", "|", "'", "\""]

# features 에서 -1과 -999는 유효하지 않은 값을 나타내는 것으로 보임
NON_EMBED_FEATURE_INVALID_VALUE = -1
EMBED_FEATURE_INVALID_VALUE = -999

DEFAULT_SAMPLING_SIZE = 20

EPSILON = 1e-12


def make_self_features_from(table_df: pd.DataFrame) -> Tuple[NDArray[Any], Dict[str, str]]:
    """Extract features from table columns.

    Returns:
         Tuple[np.ndarray, Dict[str, str]]: Features and column classifications.
    """
    feature_array = []
    column_types = {}

    for column in table_df.columns:
        # TODO: why use "Unnamed:"
        if "Unnamed:" in column:
            continue

        feature, data_type = extract_features(table_df[column].tolist())
        feature_array.append(feature.reshape(1, -1))
        column_types[column] = data_type.name

    if len(feature_array) == 0:
        raise ValueError(f"No features extracted. Check your table: {table_df}.")

    # get each columns features and concatenate all features
    # will make (columns_length, feature_matrix_len)
    # should be (len(columns), 792)
    features = np.vstack(feature_array)

    logging.debug(f"{__name__}: {features.shape}")

    return features, column_types


# REMINDER: use ONLY data_list as Column
def extract_features(data_list: List[Any]) -> Tuple[NDArray[Any], DataTypes]:
    """Extract features from the given data.

    Args:
        data_list (List[Any]): data can be column or list.

    Returns:
        Tuple[np.array, DataTypes]: Extract features and data type from the given data.
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

    return output_features, data_type


def extract_numeric(data_list: List[Any]) -> List[float]:
    """Extract Numeric from the given data.

    Notes:
        unit 간 우선순위가 존재하지 않아, "3亿5万" 같은 케이스에서 亿 대신 万가 사용되어 원본 값과 크게 차이 날 수 있음.
        unit 이 존재한다면 이후의 값이 유실됨, "3万5"의 경우 30000.0 으로 변환됨.
        한글에서 "1억 5천만"과 같이 숫자 내 whitespace를 사용하는 경우 drop 됨.
        "만", "亿" 과 같은 unit 사용된 문자열의 경우 drop 됨.

    Args:
        data_list: DataType.NUMERIC 이 검증된 데이터

    Returns:
        List[float]: Extracts numeric part(including float) from string list

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

        # find all numeric parts as [List[tuple[str, str]]
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
        for unit_key in constants.UNIT_DICT.keys():
            if unit_key in data:
                unit = constants.UNIT_DICT[unit_key]
                break

        numeric_list.append(float_part * unit)

    return numeric_list


def calculate_numeric_features(data_list: List[float]) -> NDArray[Any]:
    """Calculate numeric features from given data.

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


def calculate_character_features(data_list: List[Any]) -> NDArray[Any]:
    """Calculate character features from given data.

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

    epsilon = np.array([EPSILON] * len(data_list))

    whitespace_ratios = np.array(whitespace_ratios) + epsilon
    punctuation_ratios = np.array(punctuation_ratios) + epsilon
    special_character_ratios = np.array(special_character_ratios) + epsilon
    numeric_ratios = np.array(numeric_ratios) + epsilon

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


def deep_embedding(data_list: List[Any]) -> NDArray[Any]:
    """Get deep embedding from given data.

    Notes:
        Deep Embedding Feature 는 data 를 SentenceTransformer 로 encoding 후 값들의 mean 을 취함.
        20 개의 데이터를 Sampling 하여 사용.

    Returns:
        np.ndarray: Extracts deep embedding features from the given data using sentence-transformers.
    """
    # TODO: DEFAULT_SAMPLING_SIZE 미만일 떄 dimension 유지되는지?
    if len(data_list) >= DEFAULT_SAMPLING_SIZE:
        data_list = random.sample(data_list, DEFAULT_SAMPLING_SIZE)  # safe random checked

    # TODO: use Depends
    model = SentenceTransformer.get()

    # str encode
    # TODO: check side effect
    embeddings = np.array(model.encode(data_list))

    return np.mean(embeddings, axis=0)


def get_datatype_feature(data_type: DataTypes) -> NDArray[Any]:
    """데이터 유형 피쳐 생성.

    Returns:
    Make data type feature one hot encoding
    """
    # TODO: rely on enum len. when datatypes changes make XGBoost Length err.
    data_type_feature = np.zeros(len(DataTypes) - 1)
    data_type_feature[data_type.value] = 1

    return data_type_feature


def get_data_numeric_feature(data_list: List[Any], data_type: DataTypes) -> NDArray[Any]:
    """Numeric feature 생성.

    Returns:
    np.ndarray: Get numeric features if the data MAINLY_NUMERIC or STRICT_NUMERIC, else invalid values matrix.
    """
    if data_type == DataTypes.MAINLY_NUMERIC or data_type == DataTypes.STRICT_NUMERIC:
        data_numeric = extract_numeric(data_list)
        numeric_features = calculate_numeric_features(data_numeric)
    else:
        # dont use numeric features, give default  invalid values
        numeric_features = np.array([NON_EMBED_FEATURE_INVALID_VALUE] * constants.NUMERIC_FEATURES_DIMENSION)

    return numeric_features


def get_character_feature(data_list: List[Any], data_type: DataTypes) -> NDArray[Any]:
    """Character feature 생성.

    Returns:
    np.ndarray: Give character features if the data is STRING or MAINLY_NUMERIC, else invalid values matrix.
    """
    if data_type == DataTypes.STRING or data_type == DataTypes.MAINLY_NUMERIC:
        character_feature = calculate_character_features(data_list)
    else:
        character_feature = np.array([NON_EMBED_FEATURE_INVALID_VALUE] * constants.CHARACTER_FEATURES_DIMENSION)

    return character_feature


def get_deep_embedding_feature(data_list: List[Any], data_type: DataTypes) -> NDArray[Any]:
    """Deep Embedding feature 생성.

    Returns:
    np.ndarray: Give deep embeddings if the data is STRING or MAINLY_NUMERIC, else invalid values matrix.
    """
    if data_type == DataTypes.STRING or data_type == DataTypes.MAINLY_NUMERIC:
        deep_embedding_feature = deep_embedding(data_list)
    else:
        deep_embedding_feature = np.array([EMBED_FEATURE_INVALID_VALUE]
                                          * constants.DEEP_EMBEDDING_FEATURES_DIMENSION)

    return deep_embedding_feature
