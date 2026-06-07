# Biometric and Face Recognition Based Fest Entry Management System

This is a complete Python + Machine Learning + Web Development college project for fest entry verification. The project is built with Flask, SQLite, OpenCV, LBPH face recognition, HTML, CSS, and JavaScript.

## Upgrade Note

The latest upgrade adds:

- fixed `Graphic Era` college identity
- mandatory department dropdown
- multiple face samples for better recognition
- QR code generation and QR-based gate verification
- `Pending -> Department Verified -> Approved -> Rejected` workflow
- gate log method tracking for `Face`, `QR`, `Both`, and `Manual`

See [UPGRADE_GUIDE.md](C:\Users\Teslacoil\Documents\biometric based entry system\UPGRADE_GUIDE.md) for the detailed architecture and implementation changes.

## Project Abstract

The system helps colleges manage fest registrations and gate entry in a smarter way. Participants register online in advance, upload or capture a face photo, and wait for admin approval. At the event gate, the system verifies the participant using webcam-based face recognition and records the entry time automatically. It also prevents duplicate entry and supports manual verification through registration ID or name search.

## Main Parts

1. Registration website
2. Admin dashboard
3. Entry verification panel

## Major Features

- Modern homepage and responsive UI
- Online participant registration form
- Webcam photo capture and file upload support
- Admin login system
- Admin approval, rejection, edit, and delete options
- Event management panel
- Search and filter registrations
- CSV and Excel export
- Webcam-based face recognition for gate verification
- Duplicate entry prevention
- Unknown person detection
- Daily entry report generation

## Technologies Used

- Python
- Flask
- SQLite
- OpenCV with LBPH face recognizer
- NumPy
- Pandas
- HTML, CSS, JavaScript


This project uses OpenCV LBPH face recognition instead of `face_recognition` and `dlib`, so it is easier to install and present on Windows systems.
