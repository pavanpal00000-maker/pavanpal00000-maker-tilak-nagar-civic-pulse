from pathlib import Path
import sqlite3

# Keep the database in the project root.
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_FOLDER / "complaints.db"


def get_connection():
    # Open a connection to the complaint database.
    return sqlite3.connect(DATABASE_FILE)


def setup_database():
    # Create the tables when the app runs for the first time.
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                complaint_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                photo_name TEXT,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS complaint_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT NOT NULL,
                status TEXT NOT NULL,
                note TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)


def save_complaint(complaint):
    # Save the complaint details in the database.
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO complaints (
                complaint_id, created_at, category, description,
                location, photo_name, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint["complaint_id"],
            complaint["created_at"],
            complaint["category"],
            complaint["description"],
            complaint["location"],
            complaint["photo_name"],
            complaint["status"],
            complaint["updated_at"],
        ))

        # Add the first status to the history.
        connection.execute("""
            INSERT INTO complaint_history (
                complaint_id, status, note, changed_at
            ) VALUES (?, ?, ?, ?)
        """, (
            complaint["complaint_id"],
            complaint["status"],
            "Complaint registered on this project portal.",
            complaint["created_at"],
        ))


def find_complaint(complaint_id):
    # Return one complaint using its ID.
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            (complaint_id.strip().upper(),),
        ).fetchone()


def get_complaint_history(complaint_id):
    # Return all status updates for one complaint.
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute("""
            SELECT status, note, changed_at
            FROM complaint_history
            WHERE complaint_id = ?
            ORDER BY id
        """, (complaint_id.strip().upper(),)).fetchall()


def update_complaint_status(complaint_id, status, note, changed_at):
    # Update the current status and save the status history.
    with get_connection() as connection:
        connection.execute("""
            UPDATE complaints
            SET status = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (status, changed_at, complaint_id))

        connection.execute("""
            INSERT INTO complaint_history (
                complaint_id, status, note, changed_at
            ) VALUES (?, ?, ?, ?)
        """, (complaint_id, status, note, changed_at))


def get_all_complaints():
    # Return all complaints for the admin page.
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute("""
            SELECT complaint_id, created_at, category, location, status, updated_at
            FROM complaints
            ORDER BY created_at DESC
        """).fetchall()
