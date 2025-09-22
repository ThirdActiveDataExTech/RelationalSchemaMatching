class Constants:
    """패키지 내에서 공통으로 사용되는 상수."""

    # TEXT CONSTANTS
    # 한자 번체, 신자체, 영어 dataset에서 숫자 단위를 변환하기 위한 dict
    UNIT_DICT = {"万": 10000, "亿": 100000000, "萬": 10000, "億": 100000000, "K+": 1000, "M+": 1000000,
                 "B+": 1000000000}

    # DIMENSIONAL CONSTANTS
    NUMERIC_FEATURES_DIMENSION = 6
    CHARACTER_FEATURES_DIMENSION = 8
    DEEP_EMBEDDING_FEATURES_DIMENSION = 768

    ADDITIONAL_FEATURE_DIMENSION = 6  # not sure


constants = Constants()
