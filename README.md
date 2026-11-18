# AI Attendance Management System

This project is a simple beginner-friendly Flask app for managing student attendance.

## Folder structure

- app.py
  - Main Flask app
  - Handles login, adding students, marking attendance, and reporting
- templates/
  - login.html
  - add_student.html
  - mark_attendance.html
  - report.html
  - base.html
- static/
  - style.css
- attendance_system.db
  - SQLite database file created automatically
- requirements.txt
  - Python packages needed for the project

## How it works

1. Login page
   - The app starts on the login page.
   - Default admin login: admin / admin123

2. Add Student
   - You can add students by name and department.

3. Mark Attendance
   - You choose a student and mark them Present or Absent.

4. Attendance Report
   - The report shows each student's attendance percentage.
   - The built-in AI helper flags students below 75%.

## File explanations

### app.py
- get_db_connection(): opens the SQLite database.
- init_db(): creates the tables and inserts the default admin user.
- calculate_attendance_percentage(student_id): counts present and total records, then calculates the percentage.
- find_low_attendance_students(): finds students below 75% attendance.
- login_required(): protects pages that need login.
- Routes:
  - /login: login page
  - /students/add: add student page
  - /attendance/mark: mark attendance page
  - /report: attendance report page

### templates/base.html
- Shared layout for the whole app.
- Contains the navigation menu and flash messages.

### templates/login.html
- Simple login form.

### templates/add_student.html
- Form to add a new student.

### templates/mark_attendance.html
- Form to mark attendance as Present or Absent.

### templates/report.html
- Displays attendance results and alerts students below 75%.

### static/style.css
- Simple style for the user interface.

## Setup instructions

1. Open a terminal in this project folder.
2. Create a Python virtual environment:
   python -m venv .venv
3. Activate the environment:
   .\.venv\Scripts\activate
4. Install the packages:
   pip install -r requirements.txt
5. Start the app:
   python app.py
6. Open this address in your browser:
   http://127.0.0.1:5000/login

## Simple AI feature

The AI feature is intentionally simple:
- It checks every student's attendance percentage.
- If the percentage is below 75%, it warns the user on the report page.

You can improve this later by adding machine learning or a more advanced rule system.
