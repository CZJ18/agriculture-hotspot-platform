import unittest

from app.video.parsers.generic import GenericVideoParser


class VideoParserTests(unittest.TestCase):
    def test_generic_parser_extracts_open_graph_video_metadata(self) -> None:
        html = """
        <html>
          <head>
            <meta property="og:title" content="Public video title" />
            <meta property="og:description" content="Public video description" />
            <meta property="og:image" content="https://example.com/cover.jpg" />
            <meta property="og:video" content="https://cdn.example.com/video.mp4" />
          </head>
        </html>
        """

        metadata = GenericVideoParser().parse("https://example.com/watch/1", html)

        self.assertEqual(metadata.title, "Public video title")
        self.assertEqual(metadata.description, "Public video description")
        self.assertEqual(metadata.thumbnail_url, "https://example.com/cover.jpg")
        self.assertEqual(metadata.direct_video_url, "https://cdn.example.com/video.mp4")


if __name__ == "__main__":
    unittest.main()
