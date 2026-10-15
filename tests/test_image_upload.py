import unittest
from utils.image_handler import ALLOWED_TYPES, MAX_FILE_SIZE


class TestImageUpload(unittest.TestCase):
    def test_image_types_are_limited(self):
        # Only common image formats should be accepted.
        self.assertIn("jpg", ALLOWED_TYPES)
        self.assertIn("png", ALLOWED_TYPES)

    def test_photo_size_limit_is_five_mb(self):
        # Keep photo uploads small for this prototype.
        self.assertEqual(MAX_FILE_SIZE, 5 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()

