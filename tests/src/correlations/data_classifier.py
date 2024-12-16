import unittest

from app.src.correlations.data_classifier import is_url, DataTypes, classify_data_type, is_date, is_mainly_numeric, \
    is_strict_numeric
from tests.src.testcase import TestCase

URL_DICT = {
    "https://www.example.com": True,
    "http://subdomain.example.co.uk/page": True,
    "https://example.com/path/to/page?param1=value1&param2=value2": True,
    "ftp://ftp.example.org/files/": True,
    "https://www.example.com:8080": True,
    "http://123.45.67.89/": True,
    "https://example.com/path with spaces/": False,  # Spaces in URL path are generally not valid
    "http://localhost:3000": True,
    "https://www.ex-ample.com": True,
    "http://example.com#section": True,
    "https://.example.com": False,  # Leading dot in domain is not valid
    "http://example..com": False,  # Double dots in domain are not valid
    "https://www.example.com/index.html#top": True,
    "http://user:plusplus@example.com": True,
    "https://www.example.com/path/to/file.jpg": True,
    "http://example.com/?q=test&lang=en": True,
    "https://subdomain.example.com:8080/path?query=value#fragment": True,
    "http:// invalidurl.com": False,  # Space after protocol is not valid
    "https://www.exa mple.com": False,  # Space in domain name is not valid
    "http://www.example.com/path/to/page.php?id=123&user=john": True
}

DATE_DICT = {
    "2023年6月1日": True,
    "2022年12月31日": True,
    "2021年1月15日": True,
    "2022-12-31": True,
    "15/01/2021": True,
    "不是日期": True,  # SUS
    "31/12/2022": True,
    "1/15/2021": True,
    "date": False,
    "1999-12-31": True,
    "2031-01-01": True,
    "2023-06-01": True,
    "": False,
    "1,2,3": True,  # SUS
    "年月日": True,  # SUS
    "日月年": True,  # SUS
    "月日年": True,  # SUS
}

# NUMERIC_STRING, IS_STRICT_NUMERIC, IS_MAINLY_NUMERIC
NUMERIC_TUPLE: list[tuple[str, bool, bool]] = [
    ("2.5e-4", True, True),
    ("-3.14", True, True),
    ("5.9", True, True),
    ("42", True, True),
    ("1e3", True, True),
    ("0", True, True),
    ("NaN", True, False),
    ("Inf", True, False),
    ("-Inf", True, False),
    ("1,000", False, True),
    ("five", False, False),
    ("$10", False, True),
    ("50%", False, True),
    ("3rd", False, False),
    ("1K", False, True),
    ("2M", False, True),
    ("", False, False),
    ("N/A", False, False),
    ("1.2.3", False, True),
    ("1,234.56", False, True),
    ("1e-3", True, True),
    ("3.14159", True, True),
    ("-0", True, True),
    ("+42", True, True),
    (".5", True, True),
    ("½", False, False),
    ("①", False, False),
    ("二", False, False),
    ("4千", False, True),
    ("5万", False, True),
    ("10th", False, True),
    ("1,000,000", False, True),
    ("$1,234.56", False, True),
    ("75%", False, True),
    ("1.5M", False, True),
    ("2.5B", False, True)
]


class ClassifierTestCase(unittest.TestCase):

    def test_is_url(self):
        for url, valid in URL_DICT.items():
            actual = is_url([url])
            self.assertEqual(actual, valid, f"`{url}`: expected: {valid}, actual: {actual}")

    def test_is_date(self):
        for date, valid in DATE_DICT.items():
            actual = is_date([date])
            self.assertEqual(actual, valid, f"`{date}`: expected: {valid}, actual: {actual}")

    def test_is_numeric(self):
        for data, strict_numeric, mainly_numeric in NUMERIC_TUPLE:
            actual = is_mainly_numeric([data])
            self.assertEqual(actual, mainly_numeric, f"`{data}`: expected: {mainly_numeric}, actual: {actual}")

            actual = is_strict_numeric([data])
            self.assertEqual(actual, strict_numeric, f"`{data}`: expected: {strict_numeric}, actual: {actual}")

    def test_classify(self):
        valid_urls = [u for u, v in URL_DICT.items() if v]
        invalid_urls = [u for u, v in URL_DICT.items() if not v]

        valid_dates = [u for u, v in DATE_DICT.items() if v]
        invalid_dates = [u for u, v in DATE_DICT.items() if not v]

        strict_numerics = [data for data, strict_numeric, mainly_numeric in NUMERIC_TUPLE if strict_numeric]
        mainly_numerics = [data for data, strict_numeric, mainly_numeric in NUMERIC_TUPLE if mainly_numeric]
        non_numerics = [data for data, strict_numeric, mainly_numeric in NUMERIC_TUPLE if not mainly_numeric and
                        not strict_numeric]

        classify_url_test_cases = [
            TestCase("Valid Url List", valid_urls, DataTypes.URL),
            TestCase("Invalid Url List", invalid_urls, DataTypes.STRING),
            TestCase("Url Valid Ratio 50% List", [valid_urls[0]] * 5 + [invalid_urls[0]] * 5, DataTypes.STRING),
            TestCase("Url Valid Ratio 90% List", [valid_urls[0]] * 9 + [invalid_urls[0]] * 1, DataTypes.URL),

            TestCase("Valid Date List", valid_dates, DataTypes.DATE),
            TestCase("Invalid Date List", invalid_dates, DataTypes.STRING),
            TestCase("Date Valid Ratio 50% List", [valid_dates[0]] * 5 + [invalid_dates[0]] * 5, DataTypes.STRING),
            TestCase("Date Valid Ratio 90% List", [valid_dates[0]] * 9 + [invalid_dates[0]] * 1, DataTypes.DATE),

            TestCase("Strict Numeric List", strict_numerics, DataTypes.STRICT_NUMERIC),
            TestCase("Mainly Numeric List", mainly_numerics, DataTypes.MAINLY_NUMERIC),
            TestCase("Non Numeric List", non_numerics, DataTypes.STRING),
            TestCase("Strict Numeric Ratio 50% List", [strict_numerics[0]] * 5 + [non_numerics[0]] * 5,
                     DataTypes.STRING),
            TestCase("Strict Numeric Ratio 90% List", [strict_numerics[0]] * 9 + [non_numerics[0]] * 1,
                     DataTypes.MAINLY_NUMERIC),
            TestCase("Strict Numeric Ratio 95% List", [strict_numerics[0]] * 95 + [non_numerics[0]] * 5,
                     DataTypes.STRICT_NUMERIC),
        ]

        for c in classify_url_test_cases:
            actual = classify_data_type(c.data)
            self.assertEqual(actual, c.expect, f"{c.name}: expected: {c.expect}, actual: {actual}")


if __name__ == '__main__':
    unittest.main()
