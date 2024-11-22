from enum import Enum


class Strategy(str, Enum):
    ONE_TO_ONE = "one-to-one"
    ONE_TO_MANY = "one-to-many"
    MANY_TO_MANY = "many-to-many"


class MatchingModel(str, Enum):
    def __new__(cls, value, path):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.path = path
        return obj

    INITIAL = ("initial", "model/initial_model")


class CombinationType(str, Enum):
    TRAIN = "train",
    TEST = "test"


class TestType(str, Enum):
    EVALUATION = "evaluation",
    INFERENCE = "inference"
