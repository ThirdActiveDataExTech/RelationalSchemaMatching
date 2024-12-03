import unittest

from app.src.correlations.data_classifier import is_url, DataTypes, classify_data_type, is_date
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
    "http://user:password@example.com": True,
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


class ClassifierTestCase(unittest.TestCase):

    def test_is_url(self):
        for url, valid in URL_DICT.items():
            actual = is_url([url])
            self.assertEqual(actual, valid, f"{url}: expected: {valid}, actual: {actual}")

    def test_is_date(self):
        for date, valid in DATE_DICT.items():
            actual = is_date([date])
            self.assertEqual(actual, valid, f"{date}: expected: {valid}, actual: {actual}")

    def test_classify(self):
        valid_urls = [u for u, v in URL_DICT.items() if v is True]
        invalid_urls = [u for u, v in URL_DICT.items() if v is False]

        valid_dates = [u for u, v in DATE_DICT.items() if v is True]
        invalid_dates = [u for u, v in DATE_DICT.items() if v is False]

        classify_url_test_cases = [
            TestCase("Valid Url List", valid_urls, DataTypes.URL),
            TestCase("Invalid Url List", invalid_urls, DataTypes.STRING),
            TestCase("Url Valid Ratio 50% List", [valid_urls[0]] * 5 + [invalid_urls[0]] * 5, DataTypes.STRING),
            TestCase("Url Valid Ratio 90% List", [valid_urls[0]] * 9 + [invalid_urls[0]] * 1, DataTypes.URL),

            TestCase("Valid Date List", valid_dates, DataTypes.DATE),
            TestCase("Invalid Date List", invalid_urls, DataTypes.STRING),
            TestCase("Date Valid Ratio 50% List", [valid_dates[0]] * 5 + [invalid_dates[0]] * 5, DataTypes.STRING),
            TestCase("Date Valid Ratio 90% List", [valid_dates[0]] * 9 + [invalid_dates[0]] * 1, DataTypes.DATE),
        ]

        for c in classify_url_test_cases:
            actual = classify_data_type(c.data)
            self.assertEqual(actual, c.expect, f"{c.name}: expected: {c.expect}, actual: {actual}")


if __name__ == '__main__':
    unittest.main()
