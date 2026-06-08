"""
============================================================
  register.py
  Registers a new student by:
    1. Opening webcam
    2. Capturing their face photo
    3. Saving photo + student info to database
============================================================
"""

import cv2
import os
import sys

# Add parent folder to path so we can import db_helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_helper import (
    save_student, student_exists, STUDENTS_DIR
)


def capture_face_photo(name, roll_number):
    """
    Opens webcam and waits for user to press SPACE to capture photo.
    Saves the photo as database/students/<roll_number>.jpg

    Returns:
        True  — if photo was captured successfully
        False — if camera failed or user cancelled
    """
    # Open the default webcam (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam. Check if it is connected.")
        return False

    # Load OpenCV's built-in face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print(f"\n[INFO] Registering: {name} ({roll_number})")
    print("[INFO] Look at the camera. Press SPACE to capture. Press Q to cancel.")

    photo_saved = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read from webcam.")
            break

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        # Draw a green box around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, "Face Detected", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        # Show instructions on the screen
        cv2.putText(
            frame,
            f"Student: {name} | SPACE=Capture  Q=Cancel",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
        )

        cv2.imshow("Register Student - Face Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        # SPACE key — capture photo
        if key == ord(" "):
            if len(faces) == 0:
                print("[WARNING] No face detected. Please position your face in frame.")
                continue

            # Save photo as roll_number.jpg
            photo_path = os.path.join(STUDENTS_DIR, f"{roll_number}.jpg")
            cv2.imwrite(photo_path, frame)
            print(f"[SUCCESS] Photo saved: {photo_path}")
            photo_saved = True
            break

        # Q key — cancel
        elif key == ord("q") or key == 27:
            print("[INFO] Registration cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return photo_saved


def register_student(name, roll_number, department):
    """
    Full registration flow:
    1. Check if student already exists
    2. Capture face photo via webcam
    3. Save student info to CSV

    Returns:
        (success: bool, message: str)
    """
    # Validate inputs
    if not name.strip() or not roll_number.strip() or not department.strip():
        return False, "All fields (Name, Roll Number, Department) are required."

    # Check for duplicate roll number
    if student_exists(roll_number):
        return False, f"Student with Roll Number '{roll_number}' is already registered."

    # Capture photo
    photo_taken = capture_face_photo(name.strip(), roll_number.strip())

    if not photo_taken:
        return False, "Photo capture failed or was cancelled."

    # Save to CSV
    save_student(name.strip(), roll_number.strip(), department.strip())
    return True, f"Student '{name}' registered successfully!"
