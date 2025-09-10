# Employee-Attendance-System
A facial recognition-based employee clock-in/out system. This will include a webcam interface, facial recognition, and dashboard to view attendance records.

# Employee Attendance System

A simple Employee Attendance System built with Flask (Python), SQLite, and HTML/CSS/JavaScript.

## Features

- Employee registration and login
- Clock in and clock out
- Attendance dashboard for employees
- Admin panel for managing and viewing all attendance

## How to Run

1. Install dependencies in the `backend` directory:
   ```
   pip install -r requirements.txt
   ```
2. Run the Flask server:
   ```
   python app.py
   ```
3. Access the app at `http://localhost:5000`

## Directory Structure

- `backend/` - Flask backend and database
- `frontend/` - HTML templates and static assets

> For demo, admin registration can be done by manually setting `is_admin=True` in the database.

employee-attendance-system/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── style.css
│   │   └── main.js
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       └── admin.html
├── README.md
