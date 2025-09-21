from enum import Enum


class Strategy(str, Enum):
    """Matching strategy options."""
    ONE_TO_ONE = "one-to-one"
    ONE_TO_MANY = "one-to-many"
    MANY_TO_MANY = "many-to-many"


class MatchingModel(str, Enum):
    """Matching model enumeration with file paths."""
    __slots__ = ('path',)

    def __new__(cls, value: str, path: str):
        """Create new MatchingModel instance.

        Args:
            value: String value of the enum.
            path: File path to the model.

        Returns:
            MatchingModel: New instance.
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, value: str, path: str):
        """Initialize MatchingModel.

        Args:
            value: String value of the enum.
            path: File path to the model.
        """
        self.path = path

    INITIAL = ("initial", "model/initial_model")
