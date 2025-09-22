import unittest

import numpy as np
import pandas as pd

from app.src.correlations.data_cleaner import drop_na_columns


class CleanerTestCase(unittest.TestCase):
    na_test_cases = [
        {
            "name": "Basic case with NA and '--' values",
            "data": {
                "A": [1, 2, np.nan, 4, '--'],
                "B": ['--', '--', '--', '--', '--'],
                "C": [1, 2, 3, 4, 5]
            },
            "expected_columns": ["A", "C"]
        },
        {
            "name": "All columns valid",
            "data": {
                "X": [1, 2, 3, 4, 5],
                "Y": ['a', 'b', 'c', 'd', 'e'],
                "Z": [1.1, 2.2, 3.3, 4.4, 5.5]
            },
            "expected_columns": ["X", "Y", "Z"]
        },
        {
            "name": "All columns should be dropped",
            "data": {
                "P": [np.nan, np.nan, np.nan, np.nan, np.nan],
                "Q": ['--', '--', '--', '--', '--'],
                "R": [np.nan, '--', np.nan, '--', np.nan]
            },
            "expected_columns": []
        },
        {
            "name": "Mixed case with one value column",
            "data": {
                "A": [1, np.nan, np.nan, np.nan, np.nan],
                "B": ['--', '--', '--', '--', 'x'],
                "C": [1, 2, 3, 4, 5],
                "D": ['--', '--', '--', '--', '--'],
            },
            "expected_columns": ["A", "B", "C"]
        },
        {
            "name": "Case with empty DataFrame",
            "data": {},
            "expected_columns": []
        }
    ]

    def test_drop_na_columns(self):
        for case in self.na_test_cases:
            print(f"Case: {case['name']}")
            df = pd.DataFrame(case['data'])
            result = drop_na_columns(df)
            self.assertEqual(list(result.columns), case['expected_columns'],
                             f"expected: {case['expected_columns']}, actual: {list(result.columns)}")


if __name__ == '__main__':
    unittest.main()
