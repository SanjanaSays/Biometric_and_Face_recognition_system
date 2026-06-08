"""
============================================================
  recognize.py
  Live face recognition engine:
    - Loads all registered student photos
    - Opens webcam
    - Matches detected faces to known students
    - Logs every entry with timestamp
    - Saves photos of unknown faces
============================================================
"""

import cv2
import face_recognition
import numpy as np
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_helper import (
    log_entry, get_student_by_name,
    STUDENTS_DIR, UNKNOWN_DIR
)


def load_known_faces():
    """
    Read all photos from database/students/ folder.
    Compute a face encoding (a 128-number fingerprint) for each.

    Returns:
        known_encodings — list of face encodings
        known_names     — list of student names matching each encoding
        known_rolls     — list of roll numbers matching each encoding
    """
    known_encodings = []
    known_names     = []
    known_rolls     = []

    if not os.path.exists(STUDENTS_DIR):
        return known_encodings, known_names, known_rolls

    photo_files = [
        f for f in os.listdir(STUDENTS_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not photo_files:
        print("[WARNING] No student photos found. Please register students first.")
        return known_encodings, known_names, known_rolls

    print(f"[INFO] Loading {len(photo_files)} registered student(s)...")

    for photo_file in photo_files:
        roll_number = os.path.splitext(photo_file)[0]   # filename = roll number
        photo_path  = os.path.join(STUDENTS_DIR, photo_file)

        # Load image and find face encodings
        image     = face_recognition.load_image_file(photo_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])
            known_rolls.append(roll_number)

            # Look up the student's name from CSV
            student = get_student_by_name_by_roll(roll_number)
            known_names.append(student if student else roll_number)

            print(f"  ✓ Loaded: {known_names[-1]} ({roll_number})")
        else:
            print(f"  ✗ No face found in photo: {photo_file} — skipping")

    return known_encodings, known_names, known_rolls


def get_student_by_name_by_roll(roll_number):
    """Helper: look up student name from students.csv by roll number."""
    from database.db_helper import get_all_students
    students = get_all_students()
    for s in students:
        if s["Roll Number"] == roll_number:
            return s["Name"]
    return None


# ── Track who was logged recently to avoid duplicate entries ──
_recent_log = {}   # { name: last_logged_timestamp }
LOG_COOLDOWN = 10  # seconds between repeat logs for same person


def should_log(name):
    """Return True only if enough time has passed since last log for this name."""
    now = datetime.now()
    if name in _recent_log:
        elapsed = (now - _recent_log[name]).seconds
        if elapsed < LOG_COOLDOWN:
            return False
    _recent_log[name] = now
    return True


def save_unknown_face(frame, face_location):
    """Save a cropped photo of an unknown face for admin review."""
    top, right, bottom, left = face_location
    face_img  = frame[top:bottom, left:right]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = os.path.join(UNKNOWN_DIR, f"unknown_{timestamp}.jpg")
    cv2.imwrite(filename, face_img)
    return filename


def run_recognition(stop_flag=None):
    """
    Main recognition loop.
    Opens webcam, detects faces, identifies them, logs entries.

    Args:
        stop_flag — a list [False] that can be set to [True] externally to stop the loop
                    (used by the UI to stop the camera cleanly)
    """
    # Load known faces
    known_encodings, known_names, known_rolls = load_known_faces()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    print("\n[INFO] Recognition started. Press Q in the camera window to stop.\n")

    # Process every other frame to save CPU
    frame_count = 0

    while True:
        # Check if stop was requested from UI
        if stop_flag and stop_flag[0]:
            break

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 2 != 0:
            # Skip odd frames for speed
            cv2.imshow("College Entry System — Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        # ── Resize frame to 1/4 size for faster processing ──
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small   = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # ── Find all faces in this frame ──
        face_locations  = face_recognition.face_locations(rgb_small)
        face_encodings  = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            name        = "Unknown"
            roll_number = "N/A"
            color       = (0, 0, 255)   # Red for unknown
            status_text = "ACCESS DENIED"

            if known_encodings:
                # Compare this face against all known faces
                matches      = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match   = np.argmin(face_distances)

                if matches[best_match]:
                    name        = known_names[best_match]
                    roll_number = known_rolls[best_match]
                    color       = (0, 255, 0)   # Green for known
                    status_text = "ACCESS GRANTED"

            # ── Scale face location back to full size ──
            top, right, bottom, left = [v * 4 for v in face_location]

            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw name label background
            cv2.rectangle(frame, (left, bottom - 40), (right, bottom), color, cv2.FILLED)
            cv2.putText(
                frame, f"{name} | {roll_number}",
                (left + 6, bottom - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
            cv2.putText(
                frame, status_text,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (255, 255, 255), 1
            )

            # ── Log entry (with cooldown to avoid duplicates) ──
            if should_log(name):
                if name == "Unknown":
                    save_unknown_face(frame, (top, right, bottom, left))
                    log_entry("Unknown", "N/A", "ACCESS DENIED")
                    print(f"[ALERT]  Unknown face detected and saved at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    log_entry(name, roll_number, "ACCESS GRANTED")
                    print(f"[ENTRY]  {name} ({roll_number}) — ACCESS GRANTED at {datetime.now().strftime('%H:%M:%S')}")

        # ── Header overlay ──
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 45), (30, 30, 30), cv2.FILLED)
        cv2.putText(
            frame,
            "COLLEGE BIOMETRIC ENTRY SYSTEM  |  Press Q to exit",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2
        )

        cv2.imshow("College Entry System — Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Recognition stopped.")
