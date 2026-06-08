"""
============================================================
  database/db_helper.py
  Handles all data storage:
    - Saving student info
    - Logging entry records
    - Reading logs for display
============================================================
"""

import csv
import os
from datetime import datetime

# ── Folder & file paths ──────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_DIR  = os.path.join(BASE_DIR, "database", "students")
UNKNOWN_DIR   = os.path.join(BASE_DIR, "database", "unknown_faces")
LOG_FILE      = os.path.join(BASE_DIR, "database", "logs.csv")
STUDENTS_CSV  = os.path.join(BASE_DIR, "database", "students.csv")

# ── Create folders if they don't exist ───────────────────
os.makedirs(STUDENTS_DIR, exist_ok=True)
os.makedirs(UNKNOWN_DIR,  exist_ok=True)


def init_log_file():
    """Create the log CSV with headers if it doesn't exist yet."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Roll Number", "Date", "Time", "Status"])


def init_students_file():
    """Create the students CSV with headers if it doesn't exist yet."""
    if not os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Roll Number", "Department", "Registered On"])


def log_entry(name, roll_number, status="ACCESS GRANTED"):
    """
    Save an entry record to logs.csv.
    Called every time a face is recognized (or unknown).
    """
    init_log_file()
    now  = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, roll_number, date, time, status])


def save_student(name, roll_number, department):
    """Add a new student record to students.csv."""
    init_students_file()
    registered_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STUDENTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, roll_number, department, registered_on])


def get_all_logs():
    """Return all log rows as a list of dicts for display."""
    init_log_file()
    rows = []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_all_students():
    """Return all registered students as a list of dicts."""
    init_students_file()
    rows = []
    if os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    return rows


def student_exists(roll_number):
    """Check if a student with this roll number is already registered."""
    students = get_all_students()
    for s in students:
        if s["Roll Number"] == roll_number:
            return True
    return False


def get_student_by_name(name):
    """Find a student record by name."""
    students = get_all_students()
    for s in students:
        if s["Name"].lower() == name.lower():
            return s
    return None
