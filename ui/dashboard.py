"""
============================================================
  ui/dashboard.py
  Main Tkinter GUI — the control center of the app.

  Tabs:
    1. Home / Live Recognition
    2. Register Student
    3. Entry Log Viewer
    4. Student List
============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_helper import get_all_logs, get_all_students, init_log_file, init_students_file


# ── Color theme ──────────────────────────────────────────
BG_DARK    = "#0d1117"
BG_CARD    = "#161b22"
BG_BORDER  = "#30363d"
ACCENT     = "#00d4ff"
ACCENT2    = "#00ff88"
RED_ALERT  = "#ff4444"
TEXT_WHITE = "#e6edf3"
TEXT_GREY  = "#8b949e"
BTN_BG     = "#21262d"


class CollegeEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Biometric Entry System")
        self.root.geometry("900x620")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        # Initialize database files
        init_log_file()
        init_students_file()

        # Flag to stop recognition thread
        self.stop_flag = [False]
        self.recognition_thread = None

        self._build_header()
        self._build_tabs()

    # ── Header ────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_CARD, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🎓  COLLEGE BIOMETRIC ENTRY SYSTEM",
            font=("Courier New", 16, "bold"),
            fg=ACCENT, bg=BG_CARD
        ).pack(side="left", padx=20)

        tk.Label(
            header,
            text="Secure • Smart • Automated",
            font=("Courier New", 9),
            fg=TEXT_GREY, bg=BG_CARD
        ).pack(side="right", padx=20)

    # ── Tab container ─────────────────────────────────────
    def _build_tabs(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TNotebook",
            background=BG_DARK, borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=BTN_BG, foreground=TEXT_GREY,
            font=("Courier New", 10, "bold"),
            padding=[14, 8]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG_CARD)],
            foreground=[("selected", ACCENT)]
        )

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_home_tab()
        self._build_register_tab()
        self._build_logs_tab()
        self._build_students_tab()

    # ═══════════════════════════════════════════════════════
    #  TAB 1: HOME / RECOGNITION
    # ═══════════════════════════════════════════════════════
    def _build_home_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="  🏠 Home  ")

        # Status card
        card = tk.Frame(frame, bg=BG_CARD, padx=30, pady=30, relief="flat")
        card.pack(expand=True)

        tk.Label(
            card,
            text="Face Recognition Camera",
            font=("Courier New", 14, "bold"),
            fg=TEXT_WHITE, bg=BG_CARD
        ).pack(pady=(0, 6))

        tk.Label(
            card,
            text="Click START to open the webcam and begin scanning faces.\nPress Q inside the camera window to stop.",
            font=("Courier New", 9),
            fg=TEXT_GREY, bg=BG_CARD, justify="center"
        ).pack(pady=(0, 20))

        # Status label
        self.status_var = tk.StringVar(value="● Camera is OFF")
        self.status_label = tk.Label(
            card,
            textvariable=self.status_var,
            font=("Courier New", 11, "bold"),
            fg=RED_ALERT, bg=BG_CARD
        )
        self.status_label.pack(pady=(0, 20))

        # Buttons
        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack()

        self.start_btn = tk.Button(
            btn_frame,
            text="▶  START RECOGNITION",
            font=("Courier New", 11, "bold"),
            bg=ACCENT2, fg=BG_DARK, relief="flat",
            padx=20, pady=10, cursor="hand2",
            command=self._start_recognition
        )
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = tk.Button(
            btn_frame,
            text="■  STOP",
            font=("Courier New", 11, "bold"),
            bg=RED_ALERT, fg="white", relief="flat",
            padx=20, pady=10, cursor="hand2",
            state="disabled",
            command=self._stop_recognition
        )
        self.stop_btn.grid(row=0, column=1, padx=10)

        # Info boxes
        info_frame = tk.Frame(frame, bg=BG_DARK)
        info_frame.pack(pady=20, padx=30, fill="x")

        infos = [
            ("🟢", "Known Face", "Logs name + time\nShows ACCESS GRANTED"),
            ("🔴", "Unknown Face", "Saves photo to disk\nLogs ACCESS DENIED"),
            ("📋", "Auto Logging", "Every entry is saved\nto logs.csv instantly"),
        ]

        for i, (icon, title, desc) in enumerate(infos):
            box = tk.Frame(info_frame, bg=BG_CARD, padx=15, pady=12, relief="flat")
            box.grid(row=0, column=i, padx=8, sticky="nsew")
            info_frame.columnconfigure(i, weight=1)

            tk.Label(box, text=f"{icon}  {title}", font=("Courier New", 10, "bold"),
                     fg=ACCENT, bg=BG_CARD).pack()
            tk.Label(box, text=desc, font=("Courier New", 8),
                     fg=TEXT_GREY, bg=BG_CARD, justify="center").pack(pady=(4, 0))

    def _start_recognition(self):
        """Start recognition in a background thread so UI stays responsive."""
        from recognize import run_recognition

        self.stop_flag = [False]
        self.status_var.set("● Camera is ACTIVE")
        self.status_label.config(fg=ACCENT2)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.recognition_thread = threading.Thread(
            target=run_recognition,
            args=(self.stop_flag,),
            daemon=True
        )
        self.recognition_thread.start()

        # Poll thread to update UI when it ends naturally (user pressed Q)
        self.root.after(1000, self._check_recognition_thread)

    def _stop_recognition(self):
        """Signal the recognition loop to stop."""
        self.stop_flag[0] = True
        self._reset_camera_ui()

    def _check_recognition_thread(self):
        """Called every second to detect if the camera window was closed."""
        if self.recognition_thread and not self.recognition_thread.is_alive():
            self._reset_camera_ui()
        else:
            self.root.after(1000, self._check_recognition_thread)

    def _reset_camera_ui(self):
        self.status_var.set("● Camera is OFF")
        self.status_label.config(fg=RED_ALERT)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ═══════════════════════════════════════════════════════
    #  TAB 2: REGISTER STUDENT
    # ═══════════════════════════════════════════════════════
    def _build_register_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="  ➕ Register  ")

        card = tk.Frame(frame, bg=BG_CARD, padx=40, pady=30)
        card.pack(expand=True)

        tk.Label(
            card, text="Register New Student",
            font=("Courier New", 14, "bold"),
            fg=TEXT_WHITE, bg=BG_CARD
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Form fields
        fields = [
            ("Full Name",    "e.g. Rahul Sharma"),
            ("Roll Number",  "e.g. CS2024001"),
            ("Department",   "e.g. Computer Science"),
        ]

        self.reg_entries = {}
        for i, (label, placeholder) in enumerate(fields):
            tk.Label(
                card, text=label,
                font=("Courier New", 10, "bold"),
                fg=ACCENT, bg=BG_CARD, anchor="w"
            ).grid(row=i + 1, column=0, sticky="w", padx=(0, 20), pady=8)

            entry = tk.Entry(
                card, font=("Courier New", 10),
                bg=BTN_BG, fg=TEXT_WHITE,
                insertbackground=ACCENT,
                relief="flat", width=30,
                highlightthickness=1,
                highlightcolor=ACCENT,
                highlightbackground=BG_BORDER
            )
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>",  lambda e, ent=entry, ph=placeholder: self._clear_placeholder(e, ent, ph))
            entry.bind("<FocusOut>", lambda e, ent=entry, ph=placeholder: self._restore_placeholder(e, ent, ph))
            entry.grid(row=i + 1, column=1, pady=8, ipady=6, padx=4)
            self.reg_entries[label] = entry

        # Register button
        tk.Button(
            card,
            text="📸  CAPTURE PHOTO & REGISTER",
            font=("Courier New", 11, "bold"),
            bg=ACCENT, fg=BG_DARK, relief="flat",
            padx=20, pady=10, cursor="hand2",
            command=self._do_register
        ).grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

        # Result message
        self.reg_result = tk.Label(
            card, text="",
            font=("Courier New", 9),
            fg=ACCENT2, bg=BG_CARD
        )
        self.reg_result.grid(row=len(fields) + 2, column=0, columnspan=2)

    def _clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=TEXT_WHITE)

    def _restore_placeholder(self, event, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=TEXT_GREY)

    def _get_entry_value(self, label, placeholder):
        val = self.reg_entries[label].get()
        return "" if val == placeholder else val.strip()

    def _do_register(self):
        """Collect form data and run registration."""
        from register import register_student

        name       = self._get_entry_value("Full Name",   "e.g. Rahul Sharma")
        roll       = self._get_entry_value("Roll Number", "e.g. CS2024001")
        department = self._get_entry_value("Department",  "e.g. Computer Science")

        self.reg_result.config(text="Opening camera for photo capture...", fg=ACCENT)
        self.root.update()

        success, message = register_student(name, roll, department)

        if success:
            self.reg_result.config(text=f"✅ {message}", fg=ACCENT2)
            messagebox.showinfo("Registration Successful", message)
        else:
            self.reg_result.config(text=f"❌ {message}", fg=RED_ALERT)
            messagebox.showerror("Registration Failed", message)

    # ═══════════════════════════════════════════════════════
    #  TAB 3: ENTRY LOGS
    # ═══════════════════════════════════════════════════════
    def _build_logs_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="  📋 Entry Log  ")

        # Toolbar
        toolbar = tk.Frame(frame, bg=BG_CARD, pady=8)
        toolbar.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(
            toolbar, text="Entry Log — All Campus Entries",
            font=("Courier New", 11, "bold"),
            fg=TEXT_WHITE, bg=BG_CARD
        ).pack(side="left", padx=10)

        tk.Button(
            toolbar, text="🔄 Refresh",
            font=("Courier New", 9),
            bg=BTN_BG, fg=ACCENT, relief="flat",
            padx=10, pady=4, cursor="hand2",
            command=self._load_logs
        ).pack(side="right", padx=10)

        # Table
        cols = ("Name", "Roll Number", "Date", "Time", "Status")
        self.log_tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            height=18
        )
        self._style_treeview()

        for col in cols:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=140, anchor="center")

        self.log_tree.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscroll=scrollbar.set)

        self._load_logs()

    def _load_logs(self):
        """Reload log data into the table."""
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)

        logs = get_all_logs()
        for log in reversed(logs):   # Most recent first
            tag = "denied" if log.get("Status") == "ACCESS DENIED" else "granted"
            self.log_tree.insert(
                "", "end",
                values=(log["Name"], log["Roll Number"],
                        log["Date"], log["Time"], log["Status"]),
                tags=(tag,)
            )

        self.log_tree.tag_configure("granted", foreground="#00ff88")
        self.log_tree.tag_configure("denied",  foreground="#ff4444")

    # ═══════════════════════════════════════════════════════
    #  TAB 4: STUDENTS LIST
    # ═══════════════════════════════════════════════════════
    def _build_students_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="  👥 Students  ")

        toolbar = tk.Frame(frame, bg=BG_CARD, pady=8)
        toolbar.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(
            toolbar, text="Registered Students",
            font=("Courier New", 11, "bold"),
            fg=TEXT_WHITE, bg=BG_CARD
        ).pack(side="left", padx=10)

        tk.Button(
            toolbar, text="🔄 Refresh",
            font=("Courier New", 9),
            bg=BTN_BG, fg=ACCENT, relief="flat",
            padx=10, pady=4, cursor="hand2",
            command=self._load_students
        ).pack(side="right", padx=10)

        cols = ("Name", "Roll Number", "Department", "Registered On")
        self.students_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=18
        )

        for col in cols:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=180, anchor="center")

        self.students_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self._load_students()

    def _load_students(self):
        for row in self.students_tree.get_children():
            self.students_tree.delete(row)

        students = get_all_students()
        for s in students:
            self.students_tree.insert(
                "", "end",
                values=(s["Name"], s["Roll Number"],
                        s["Department"], s["Registered On"])
            )

    def _style_treeview(self):
        """Apply dark theme to treeview tables."""
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=BG_CARD,
            foreground=TEXT_WHITE,
            fieldbackground=BG_CARD,
            rowheight=28,
            font=("Courier New", 9)
        )
        style.configure(
            "Treeview.Heading",
            background=BTN_BG,
            foreground=ACCENT,
            font=("Courier New", 9, "bold")
        )
        style.map("Treeview", background=[("selected", BG_BORDER)])


def run_dashboard():
    """Entry point: create and launch the Tkinter window."""
    root = tk.Tk()
    app  = CollegeEntryApp(root)
    root.mainloop()
