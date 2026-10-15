from pathlib import Path
from PIL import Image
import uuid

# Set the folder where complaint photos will be stored.
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
UPLOAD_FOLDER = PROJECT_FOLDER / "complaints" / "uploads"
ALLOWED_TYPES = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024


def save_complaint_photo(uploaded_file):
    # Return an empty value when no photo was provided.
    if uploaded_file is None:
        return None

    # Check the file size before saving it.
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValueError("Photo must be 5 MB or smaller.")

    # Check the file extension.
    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_TYPES:
        raise ValueError("Use a JPG, JPEG, PNG, or WEBP photo.")

    # Open the image to check that it is a real image file.
    try:
        image = Image.open(uploaded_file)
        image.verify()
    except Exception as error:
        raise ValueError("The uploaded file is not a valid image.") from error

    # Give the saved photo a random name to avoid overwriting other photos.
    safe_name = f"{uuid.uuid4().hex}.jpg"
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # Save the uploaded photo in the private uploads folder.
    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")
    image.save(UPLOAD_FOLDER / safe_name, format="JPEG", quality=85)

    return safe_name
