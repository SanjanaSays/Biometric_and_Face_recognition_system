"""
============================================================
  COLLEGE BIOMETRIC FACE RECOGNITION ENTRY SYSTEM
  main.py — Start the application from here
============================================================
  HOW TO RUN:
    python main.py

  INSTALL LIBRARIES FIRST:
    pip install opencv-python face_recognition numpy pillow
============================================================
"""

from ui.dashboard import run_dashboard

if __name__ == "__main__":
    print("=" * 50)
    print("  College Biometric Entry System Starting...")
    print("=" * 50)
    run_dashboard()
