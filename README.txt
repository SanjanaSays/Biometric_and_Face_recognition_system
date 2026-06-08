============================================================
  COLLEGE BIOMETRIC FACE RECOGNITION ENTRY SYSTEM
  README — Read This First!
============================================================

PROJECT OVERVIEW:
  A desktop application that uses your webcam to detect and
  recognize student faces for secure college entry logging.

------------------------------------------------------------
STEP 1: INSTALL PYTHON LIBRARIES
------------------------------------------------------------

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

    pip install opencv-python face_recognition numpy pillow

  NOTE: 'face_recognition' may take a few minutes to install.
  It requires cmake and dlib. If it fails, try:
    pip install cmake
    pip install dlib
    pip install face_recognition

------------------------------------------------------------
STEP 2: RUN THE APP
------------------------------------------------------------

  Navigate to this folder in your terminal, then run:

    python main.py

------------------------------------------------------------
HOW TO USE THE APP:
------------------------------------------------------------

  1. GO TO "Register" TAB
     - Enter student's Full Name, Roll Number, Department
     - Click "CAPTURE PHOTO & REGISTER"
     - A camera window opens — look at the camera
     - Press SPACEBAR to take the photo
     - Press Q to cancel

  2. GO TO "Home" TAB
     - Click "START RECOGNITION"
     - The webcam opens and scans faces in real-time
     - Known students → GREEN box → ACCESS GRANTED → logged
     - Unknown faces → RED box → ACCESS DENIED → photo saved
     - Press Q in the camera window to stop

  3. VIEW LOGS
     - Go to "Entry Log" tab
     - All entries shown with name, roll no, date, time, status
     - Click Refresh to see latest entries

  4. VIEW STUDENTS
     - Go to "Students" tab to see all registered students

------------------------------------------------------------
PROJECT FOLDER STRUCTURE:
------------------------------------------------------------

  college_entry_system/
  ├── main.py              ← Run this to start the app
  ├── register.py          ← Student registration logic
  ├── recognize.py         ← Live face recognition engine
  ├── README.txt           ← This file
  ├── database/
  │   ├── students/        ← Student face photos stored here
  │   ├── unknown_faces/   ← Unknown face snapshots saved here
  │   ├── logs.csv         ← All entry records
  │   └── students.csv     ← Registered student info
  └── ui/
      └── dashboard.py     ← Tkinter GUI

------------------------------------------------------------
TECHNOLOGIES USED:
------------------------------------------------------------
  - Python 3.x
  - OpenCV         (webcam + face detection)
  - face_recognition (face matching via 128-point encoding)
  - Tkinter        (desktop GUI — built into Python)
  - CSV            (lightweight data storage)

------------------------------------------------------------
FUTURE IMPROVEMENTS (for report):
------------------------------------------------------------
  - Add RFID card + face dual authentication
  - Send SMS alert on unknown face detection
  - Use a database (SQLite) instead of CSV
  - Deploy on Raspberry Pi with camera module
  - Web dashboard for remote admin access
  - Night-mode IR camera support

============================================================
  Built for College Project Submission
============================================================
