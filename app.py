import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "attendance-secret-key"
DB_NAME = "attendance_system.db"


# -------------------------
# Database helpers
# -------------------------
def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist yet."""
    conn = get_db_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            );

            INSERT OR IGNORE INTO users (username, password)
            VALUES ('admin', 'admin123');
            """
        )
        conn.commit()
    finally:
        conn.close()


init_db()


# -------------------------
# Attendance helpers
# -------------------------
def calculate_attendance_percentage(student_id):
    """Return attendance percentage for one student."""
    conn = get_db_connection()

    total_records = conn.execute(
        "SELECT COUNT(*) AS total FROM attendance WHERE student_id = ?",
        (student_id,),
    ).fetchone()["total"]

    present_records = conn.execute(
        "SELECT COUNT(*) AS present FROM attendance WHERE student_id = ? AND status = 'Present'",
        (student_id,),
    ).fetchone()["present"]

    conn.close()

    if total_records == 0:
        return 0

    percentage = (present_records / total_records) * 100
    return round(percentage, 1)


def find_low_attendance_students():
    """Return students whose attendance is below 75%."""
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    low_students = []

    for student in students:
        percent = calculate_attendance_percentage(student["id"])
        if percent < 75:
            low_students.append({
                "id": student["id"],
                "name": student["name"],
                "department": student["department"],
                "percentage": percent,
            })

    conn.close()
    return low_students


# -------------------------
# Login helper
# -------------------------
def login_required(view_function):
    """Simple page guard for protected pages."""
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login_page"))
        return view_function(*args, **kwargs)

    return wrapper


# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    """Show the login page first, then the dashboard after login."""
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Login page for the admin user."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful.")
            return redirect(url_for("dashboard_page"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session and return to login."""
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login_page"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Create a personal user account."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.")
            return redirect(url_for("register_page"))

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if existing_user:
            conn.close()
            flash("That username already exists. Please choose another one.")
            return redirect(url_for("register_page"))

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        conn.commit()
        user_id = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()["id"]
        conn.close()

        session["user_id"] = user_id
        session["username"] = username
        flash("Account created successfully. You are now logged in.")
        return redirect(url_for("dashboard_page"))

    return render_template("register.html")


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student_page():
    """Add a new student to the database."""
    if request.method == "POST":
        student_name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not student_name or not department:
            flash("Please fill in both fields.")
            return redirect(url_for("add_student_page"))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO students (name, department) VALUES (?, ?)",
            (student_name, department),
        )
        conn.commit()
        conn.close()

        flash("Student added successfully.")
        return redirect(url_for("add_student_page"))

    return render_template("add_student.html")


@app.route("/attendance/mark", methods=["GET", "POST"])
@login_required
def mark_attendance_page():
    """Mark a student as present or absent for today."""
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        status = request.form.get("status")
        attendance_date = request.form.get("attendance_date") or str(date.today())

        student = None
        if student_id:
            try:
                student = conn.execute(
                    "SELECT id FROM students WHERE id = ?",
                    (int(student_id),),
                ).fetchone()
            except (TypeError, ValueError):
                student = None

        if not student or status not in ("Present", "Absent"):
            flash("Please choose a valid student and attendance status.")
            conn.close()
            return redirect(url_for("mark_attendance_page"))

        conn.execute(
            "INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
            (student["id"], attendance_date, status),
        )
        conn.commit()
        conn.close()

        flash("Attendance recorded successfully.")
        return redirect(url_for("mark_attendance_page"))

    conn.close()
    return render_template("mark_attendance.html", students=students)


@app.route("/dashboard")
@login_required
def dashboard_page():
    """Show a simple plain dashboard after login."""
    return render_template("dashboard.html")


@app.route("/report")
@login_required
def report_page():
    """Show attendance report and AI warning list."""
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()

    student_report = []
    for student in students:
        percentage = calculate_attendance_percentage(student["id"])
        student_report.append({
            "id": student["id"],
            "name": student["name"],
            "department": student["department"],
            "percentage": percentage,
        })

    low_students = find_low_attendance_students()
    conn.close()

    return render_template(
        "report.html",
        student_report=student_report,
        low_students=low_students,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
