import unittest

from app.src.correlations.data_classifier import is_url, DataTypes, classify_data_type
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

VALID_URLS = [u for u, v in URL_DICT.items() if v is True]
INVALID_URLS = [u for u, v in URL_DICT.items() if v is False]


class ClassifierTestCase(unittest.TestCase):
    classify_url_test_cases = [
        TestCase("Valid Url List", VALID_URLS, DataTypes.URL),
        TestCase("Invalid Url List", INVALID_URLS, DataTypes.STRING),
        TestCase("Valid Ratio 50% List", [VALID_URLS[0]] * 5 + [INVALID_URLS[0]] * 5, DataTypes.STRING),
        TestCase("Valid Ratio 90% List", [VALID_URLS[0]] * 9 + [INVALID_URLS[0]] * 1, DataTypes.URL),
    ]

    def test_is_url(self):
        for url, valid in URL_DICT.items():
            actual = is_url([url])
            self.assertEqual(actual, valid, f"{url}: expected: {valid}, actual: {actual}")

    def test_classify_url(self):
        for c in self.classify_url_test_cases:
            actual = classify_data_type(c.data)
            self.assertEqual(actual, c.expect, f"{c.name}: expected: {c.expect}, actual: {actual}")


if __name__ == '__main__':
    unittest.main()
