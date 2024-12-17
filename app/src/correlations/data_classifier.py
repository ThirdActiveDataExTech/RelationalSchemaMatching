import logging
import re
from enum import Enum
from typing import Any

import validators
from dateutil.parser import parse as parse_date

from app.src.correlations.constants import constants

DATE_DICT = {"月", "日", "年"}

DATE_RATIO = 0.9
URL_RATIO = 0.9
NUMERIC_PART_RATIO = 0.5
STRICT_NUMERIC_RATIO = 0.95
MAINLY_NUMERIC_RATIO = 0.9


class DataTypes(Enum):
    URL = 0,
    MAINLY_NUMERIC = 1,
    DATE = 2,
    STRING = 3,
    # TODO: replace 1
    STRICT_NUMERIC = 1

    def __len__(self):
        return len(self.__class__.__members__)


def classify_data_type(data_list: list[Any]) -> DataTypes:
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


def is_url(data_list: list[Any]) -> bool:
    """

    Returns:
        bool: True if data_list contains url strings than URL_RATIO
    """
    cnt = 0
    for data in data_list:
        if not isinstance(data, str):
            continue
        if validators.url(data, simple_host=True):
            cnt += 1

    return cnt >= URL_RATIO * len(data_list)


def is_date(data_list: list[Any]) -> bool:
    """

    Notes:
        단순히 문자열 내 DATE_DICT 가 있다면 체크됨.
        중국어 데이터 이외에 검출되지 않을 가능성 있음.

    Returns:
        bool: True if data_list contains date strings than DATE_RATIO
    """
    cnt = 0
    for data in data_list:
        if not isinstance(data, str):
            continue

        if any(date in data for date in DATE_DICT):
            cnt += 1
            continue

        try:
            parse_date(data)
            # check if the date is near to today
            # REMINDER: WHY THIS CONDITION IS EXIST?
            # if date.year < 2000 or date.year > 2030:
            #     continue
            cnt += 1
        except Exception as _:
            continue

    return cnt >= DATE_RATIO * len(data_list)


def is_strict_numeric(data_list: list[Any], verbose: bool = False) -> bool:
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

    return cnt >= STRICT_NUMERIC_RATIO * len(data_list)


def is_mainly_numeric(data_list: list[Any]) -> bool:
    """data 내 numeric part 가 정해진 비율 이상일 경우 mainly_numeric 으로 판단함

    Returns:
        bool: data_list 내의 mainly_numeric 비율이 STRICT_NUMERIC_RATIO 이상일 경우 True

    """
    cnt = 0
    for data in data_list:
        data = str(data)
        data = data.replace(",", "")

        # 백, 천, 만, K, B 등의 단위 제거
        for unit in constants.UNIT_DICT.keys():
            data = data.replace(unit, "")

        # data 내 numeric part 가 NUMERIC_PART_RATIO 이상일 경우 True
        numeric_part = re.findall(r'\d+', data)
        if len(numeric_part) > 0 and sum(len(x) for x in numeric_part) >= NUMERIC_PART_RATIO * len(data):
            cnt += 1

    return cnt >= MAINLY_NUMERIC_RATIO * len(data_list)
