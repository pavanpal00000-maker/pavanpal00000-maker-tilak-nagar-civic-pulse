-- Store complaint details separately from survey responses.
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    photo_name TEXT,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Keep a record of every status update.
CREATE TABLE IF NOT EXISTS complaint_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT NOT NULL,
    status TEXT NOT NULL,
    note TEXT,
    changed_at TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id)
);
