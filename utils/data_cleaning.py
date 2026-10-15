from pathlib import Path
import pandas as pd

# Find the project folder from this file's location.
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_FOLDER / "data" / "raw" / "survey_responses_raw.csv"
CLEAN_FILE = PROJECT_FOLDER / "data" / "processed" / "responses_clean.csv"

# These are the survey columns that contain satisfaction ratings.
RATING_COLUMNS = {
    "Water supply": "5. How satisfied are you with the regularity of water supply?",
    "Garbage collection": "6. How satisfied are you with garbage collection?",
    "Public cleanliness": "7. How satisfied are you with the cleanliness of public areas?",
    "Roads and footpaths": "8. How satisfied are you with the condition of roads and footpaths?",
    "Street lighting": "9. How satisfied are you with street lighting in your area?",
    "Drainage and sewage": "10. How satisfied are you with drainage and sewage services?",
    "Public toilets": "11. How satisfied are you with the availability and cleanliness of public toilets?",
    "Online municipal services": "12. How satisfied are you with online municipal services or complaint systems?",
}

OVERALL_COLUMN = "14. Overall, how satisfied are you with local government services in your area?"
LOCALITY_COLUMN = "2. Which locality do you live in?"
CONSENT_COLUMN = "1. Do you agree to participate in this survey?"
SUGGESTION_COLUMN = "15. Which local service needs the most urgent improvement, and what is your suggestion?"


def load_and_clean_data():
    # Read the latest raw CSV every time this function runs.
    data = pd.read_csv(RAW_FILE)

    # Remove extra spaces from text answers.
    for column in data.select_dtypes(include=["object", "string"]).columns:
        data[column] = data[column].str.strip()

    # Keep only responses where the person agreed to participate.
    data = data[data[CONSENT_COLUMN].str.lower() == "yes"].copy()

    # Convert the overall satisfaction answer to a number.
    data["Overall rating"] = pd.to_numeric(data[OVERALL_COLUMN], errors="coerce")

    # Convert service ratings such as "4 - Satisfied" into numbers.
    for service_name, column_name in RATING_COLUMNS.items():
        data[service_name] = pd.to_numeric(
            data[column_name].astype("string").str.extract(r"^\s*(\d+)")[0],
            errors="coerce",
        )

    # Save a cleaned copy so it can be used in notebooks and reports.
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(CLEAN_FILE, index=False)

    return data
