import unittest

from app.src.correlations.data_classifier import is_url, classify_data_type, DataTypes


class ClassifierTestCase(unittest.TestCase):
    url_validity = {
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

    def test_is_url(self):
        for url, valid in self.url_validity.items():
            result = is_url([url])
            self.assertEqual(result, valid, f"{url}: expected: {valid}, actual: {result}")

    def test_classify_url(self):
        url_ratio = len([v for v in self.url_validity.values() if v]) / len(self.url_validity)
        print(f'url_ratio: {url_ratio}')
        result = classify_data_type(list(self.url_validity.keys()))
        self.assertNotEqual(result, DataTypes.URL, f"urls classified as {result}")


if __name__ == '__main__':
    unittest.main()
