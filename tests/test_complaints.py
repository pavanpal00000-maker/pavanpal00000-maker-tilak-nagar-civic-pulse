import unittest
from utils.complaint_tracker import make_complaint_id, COMPLAINT_STATUSES


class TestComplaints(unittest.TestCase):
    def test_complaint_id_has_expected_prefix(self):
        # Check that each ID uses the project prefix.
        complaint_id = make_complaint_id()
        self.assertTrue(complaint_id.startswith("TNC-"))

    def test_submitted_status_is_available(self):
        # Check that a new complaint can use the Submitted status.
        self.assertIn("Submitted", COMPLAINT_STATUSES)


if __name__ == "__main__":
    unittest.main()

