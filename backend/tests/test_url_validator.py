import unittest

from app.security.url_validator import URLValidationError, validate_url


class URLValidatorTests(unittest.TestCase):
    def test_validate_url_blocks_unsafe_targets(self) -> None:
        unsafe_urls = [
            "file:///etc/passwd",
            "ftp://example.com/file.txt",
            "gopher://example.com",
            "http://localhost:8000",
            "http://127.0.0.1",
            "http://0.0.0.0",
            "http://[::1]/",
            "http://10.1.2.3",
            "http://172.16.0.1",
            "http://192.168.1.10",
            "http://169.254.169.254/latest/meta-data",
        ]

        for url in unsafe_urls:
            with self.subTest(url=url):
                with self.assertRaises(URLValidationError):
                    validate_url(url)

    def test_validate_url_allows_public_http_urls(self) -> None:
        result = validate_url("https://example.com/news?id=1")

        self.assertEqual(result.normalized_url, "https://example.com/news?id=1")
        self.assertEqual(result.hostname, "example.com")


if __name__ == "__main__":
    unittest.main()
