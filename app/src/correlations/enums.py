from enum import Enum


class Strategy(str, Enum):
    ONE_TO_ONE = 'one-to-one'
    ONE_TO_MANY = 'one-to-many'
    MANY_TO_ONE = 'many-to-one'
    MANY_TO_MANY = 'many-to-many'


class MatchingModel(str, Enum):
    INITIAL = 'initial_model'
