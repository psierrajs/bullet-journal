import unittest

from version import __version__


class VersionTests(unittest.TestCase):

    def test_version_uses_semantic_version_format(self):
        version_parts = __version__.split(".")

        self.assertEqual(len(version_parts), 3)
        self.assertTrue(
            all(part.isdigit() for part in version_parts)
        )


if __name__ == "__main__":
    unittest.main()