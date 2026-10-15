from datetime import datetime
import secrets
import string

# Keep the available complaint statuses in one place.
COMPLAINT_STATUSES = [
    "Submitted",
    "Under Review",
    "In Progress",
    "Resolved",
    "Closed",
]


def make_complaint_id():
    # Create a short unique-looking ID for this project portal.
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = "".join(secrets.choice(string.digits) for _ in range(4))
    return f"TNC-{date_part}-{random_part}"


def current_time():
    # Use one readable date and time format throughout the app.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
