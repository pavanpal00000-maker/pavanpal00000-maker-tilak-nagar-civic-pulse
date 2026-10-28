import unittest
from utils.department_mapping import DEPARTMENT_MAPPING
from utils.complaint_tracker import COMPLAINT_STATUSES, make_complaint_id
from utils.image_handler import ALLOWED_TYPES, MAX_FILE_SIZE
from utils.data_cleaning import RATING_COLUMNS, LOCALITY_COLUMN, load_and_clean_data


class TestUIAndCivicHelpers(unittest.TestCase):
    def test_department_mapping_coverage(self):
        # Ensure all primary civic categories map to appropriate service wings
        expected_categories = [
            "Water supply", "Garbage collection", "Public cleanliness",
            "Roads and footpaths", "Street lighting", "Drainage and sewage",
            "Public toilets", "Online municipal services", "Other"
        ]
        for cat in expected_categories:
            self.assertIn(cat, DEPARTMENT_MAPPING)
            self.assertTrue(len(DEPARTMENT_MAPPING[cat]) > 0)

    def test_complaint_statuses_ordering(self):
        # Ensure the 5 progressive stages exist in the correct sequence
        expected_sequence = ["Submitted", "Under Review", "In Progress", "Resolved", "Closed"]
        self.assertEqual(COMPLAINT_STATUSES, expected_sequence)

    def test_complaint_id_format(self):
        cid = make_complaint_id()
        self.assertTrue(cid.startswith("TNC-"))
        parts = cid.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[1]), 8)  # YYYYMMDD

    def test_data_cleaning_loading(self):
        df = load_and_clean_data()
        self.assertFalse(df.empty)
        self.assertIn("Overall rating", df.columns)
        self.assertIn(LOCALITY_COLUMN, df.columns)
        for s in RATING_COLUMNS:
            self.assertIn(s, df.columns)

    def test_complaint_admin_edit_and_delete(self):
        from database.db import save_complaint, find_complaint, update_complaint_full, delete_complaint, get_complaint_history
        test_id = "TNC-TEST-ADMIN-01"
        save_complaint({
            "complaint_id": test_id,
            "created_at": "2026-10-16 10:00:00",
            "category": "Water supply",
            "description": "Original description",
            "location": "Tilak Nagar Station",
            "photo_name": None,
            "status": "Submitted",
            "updated_at": "2026-10-16 10:00:00"
        })

        # Test edit
        update_complaint_full(
            test_id,
            "Garbage collection",
            "Shell Colony Road",
            "Updated description after admin verification",
            "In Progress",
            "Forwarded to Ward L SWM team",
            "2026-10-16 10:30:00"
        )

        c = find_complaint(test_id)
        self.assertIsNotNone(c)
        self.assertEqual(c["category"], "Garbage collection")
        self.assertEqual(c["location"], "Shell Colony Road")
        self.assertEqual(c["description"], "Updated description after admin verification")
        self.assertEqual(c["status"], "In Progress")

        # Test history
        history = get_complaint_history(test_id)
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[-1]["note"], "Forwarded to Ward L SWM team")

        # Test delete
        delete_complaint(test_id)
        self.assertIsNone(find_complaint(test_id))

    def test_image_saving_and_rejection(self):
        import io
        from pathlib import Path
        from PIL import Image
        from utils.image_handler import save_complaint_photo

        # 1. Test None returns None
        self.assertIsNone(save_complaint_photo(None))

        # 2. Test invalid extension
        fake_pdf = io.BytesIO(b"fake pdf content")
        fake_pdf.name = "document.pdf"
        fake_pdf.size = len(fake_pdf.getbuffer())
        with self.assertRaises(ValueError):
            save_complaint_photo(fake_pdf)

        # 3. Test valid JPEG image saving
        img = Image.new("RGB", (60, 60), color="blue")
        img_io = io.BytesIO()
        img.save(img_io, format="JPEG")
        img_io.name = "photo.jpg"
        img_io.size = len(img_io.getbuffer())
        saved_name = save_complaint_photo(img_io)
        self.assertIsNotNone(saved_name)
        saved_file = Path("complaints/uploads") / saved_name
        self.assertTrue(saved_file.exists())
        saved_file.unlink()  # Clean up test file

    def test_admin_password_hash(self):
        import hashlib
        import hmac
        expected_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
        calculated_hash = hashlib.sha256("admin123".encode("utf-8")).hexdigest()
        self.assertTrue(hmac.compare_digest(calculated_hash, expected_hash))


if __name__ == "__main__":
    unittest.main()


