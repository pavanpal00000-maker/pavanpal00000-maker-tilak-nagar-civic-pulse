from pathlib import Path
import sqlite3
import contextlib

# Keep the database in the project root.
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_FOLDER / "complaints.db"


@contextlib.contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def setup_database():
    # Create the tables when the app runs for the first time.
    with get_db() as connection:
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
    seed_initial_demo_complaints()



def seed_initial_demo_complaints():
    # Insert realistic sample complaints if the database is currently empty.
    with get_db() as connection:
        count = connection.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        if count == 0:
            sample_data = [
                (
                    "TNC-20261018-3412",
                    "2026-10-18 09:15:00",
                    "Roads and footpaths",
                    "Multiple deep potholes near Building No. 45, Road No. 3 causing traffic congestion.",
                    "Building No. 45, Road No. 3, Tilak Nagar, Chembur",
                    None,
                    "In Progress",
                    "2026-10-21 14:30:00",
                    [
                        ("Submitted", "Complaint registered via citizen portal.", "2026-10-18 09:15:00"),
                        ("Under Review", "Ward L road engineering wing notified; site inspection assigned.", "2026-10-19 11:20:00"),
                        ("In Progress", "Road maintenance crew deployed for cold-mix patch work.", "2026-10-21 14:30:00"),
                    ]
                ),
                (
                    "TNC-20261022-7890",
                    "2026-10-22 08:30:00",
                    "Public toilets",
                    "Public toilet block near Tilak Nagar Railway Station requires deep sanitization and tap repair.",
                    "Tilak Nagar Railway Station (West Exit)",
                    None,
                    "Resolved",
                    "2026-10-25 17:00:00",
                    [
                        ("Submitted", "Complaint registered via citizen portal.", "2026-10-22 08:30:00"),
                        ("In Progress", "Sanitation crew deployed by M-West Ward health department.", "2026-10-23 10:00:00"),
                        ("Resolved", "Plumbing fixtures repaired and deep sanitization completed.", "2026-10-25 17:00:00"),
                    ]
                ),
                (
                    "TNC-20261026-1145",
                    "2026-10-26 18:45:00",
                    "Street lighting",
                    "Four sodium streetlights off along Sahakar Cinema lane towards Tilak Nagar ground.",
                    "Sahakar Cinema Lane, Tilak Nagar",
                    None,
                    "Submitted",
                    "2026-10-26 18:45:00",
                    [
                        ("Submitted", "Complaint registered on this project portal.", "2026-10-26 18:45:00"),
                    ]
                ),
            ]
            for cid, c_at, cat, desc, loc, photo, status, u_at, hist in sample_data:
                connection.execute("""
                    INSERT INTO complaints (
                        complaint_id, created_at, category, description,
                        location, photo_name, status, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (cid, c_at, cat, desc, loc, photo, status, u_at))
                for h_status, h_note, h_time in hist:
                    connection.execute("""
                        INSERT INTO complaint_history (
                            complaint_id, status, note, changed_at
                        ) VALUES (?, ?, ?, ?)
                    """, (cid, h_status, h_note, h_time))


def save_complaint(complaint):
    # Save the complaint details in the database.
    with get_db() as connection:
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
    with get_db() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            (complaint_id.strip().upper(),),
        ).fetchone()


def get_complaint_history(complaint_id):
    # Return all status updates for one complaint.
    with get_db() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute("""
            SELECT status, note, changed_at
            FROM complaint_history
            WHERE complaint_id = ?
            ORDER BY id
        """, (complaint_id.strip().upper(),)).fetchall()


def update_complaint_status(complaint_id, status, note, changed_at):
    # Update the current status and save the status history.
    with get_db() as connection:
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
    with get_db() as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute("""
            SELECT complaint_id, created_at, category, location, description, photo_name, status, updated_at
            FROM complaints
            ORDER BY created_at DESC
        """).fetchall()


def update_complaint_full(complaint_id, category, location, description, status, note, changed_at):
    # Update full complaint details and record the audit history.
    with get_db() as connection:
        connection.execute("""
            UPDATE complaints
            SET category = ?, location = ?, description = ?, status = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (category, location, description, status, changed_at, complaint_id))

        connection.execute("""
            INSERT INTO complaint_history (
                complaint_id, status, note, changed_at
            ) VALUES (?, ?, ?, ?)
        """, (complaint_id, status, note, changed_at))


def delete_complaint(complaint_id):
    # Remove a complaint and its history records.
    with get_db() as connection:
        connection.execute("DELETE FROM complaint_history WHERE complaint_id = ?", (complaint_id,))
        connection.execute("DELETE FROM complaints WHERE complaint_id = ?", (complaint_id,))
