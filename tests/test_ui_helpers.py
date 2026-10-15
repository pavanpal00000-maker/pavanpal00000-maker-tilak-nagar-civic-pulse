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


if __name__ == "__main__":
    unittest.main()
