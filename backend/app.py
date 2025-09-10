from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Employee, Attendance
from datetime import datetime, date
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.secret_key = 'your-secret-key'
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# --- Authentication ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        emp = Employee.query.filter_by(username=username, password=password).first()
        if emp:
            session['user_id'] = emp.id
            session['role'] = emp.role
            session['username'] = emp.username
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Registration (admin/manager only) ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'role' not in session or session['role'] not in ['admin', 'manager']:
        flash("Only admin or manager can register employees.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'employee')
        department = request.form.get('department', None)
        if Employee.query.filter_by(username=username).first():
            flash('Username exists.')
            return redirect(url_for('register'))
        emp = Employee(username=username, password=password, role=role, department=department)
        db.session.add(emp)
        db.session.commit()
        flash('Employee registered.')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

# --- Role-Based Views ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = Employee.query.get(session['user_id'])
    if user.role == 'admin':
        employees = Employee.query.all()
        attendances = Attendance.query.order_by(Attendance.date.desc()).all()
        return render_template('admin_dashboard.html', user=user, employees=employees, attendances=attendances)
    elif user.role == 'manager':
        employees = Employee.query.filter_by(department=user.department).all()
        attendances = Attendance.query.join(Employee).filter(Employee.department==user.department).order_by(Attendance.date.desc()).all()
        return render_template('manager_dashboard.html', user=user, employees=employees, attendances=attendances)
    else:  # employee
        attendances = Attendance.query.filter_by(employee_id=user.id).order_by(Attendance.date.desc()).all()
        return render_template('employee_dashboard.html', user=user, attendances=attendances)

# --- API: Save Face Embedding (from frontend registration) ---

@app.route('/api/face/register', methods=['POST'])
def api_register_face():
    data = request.json
    user_id = data.get('user_id')
    face_encoding = data.get('face_encoding')
    emp = Employee.query.get(user_id)
    if emp:
        emp.face_encoding = json.dumps(face_encoding)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

# --- API: Attendance via Face Recognition ---

@app.route('/api/face/clock', methods=['POST'])
def api_face_clock():
    data = request.json
    face_encoding = data.get('face_encoding')
    action = data.get('action')  # 'in' or 'out'
    today = date.today()

    # Find matching employee (simple threshold; in production, use face_recognition.compare_faces)
    all_emps = Employee.query.filter(Employee.face_encoding != None).all()
    for emp in all_emps:
        stored_encoding = json.loads(emp.face_encoding)
        # For demo: check if embedding matches closely (here just string equal for mock)
        if stored_encoding == face_encoding:
            # Now, handle attendance
            att = Attendance.query.filter_by(employee_id=emp.id, date=today).first()
            if not att:
                att = Attendance(employee_id=emp.id, date=today)
                db.session.add(att)
            now = datetime.now().time()
            if action == 'in':
                if att.clock_in is None:
                    att.clock_in = now
                else:
                    return jsonify({"success": False, "msg": "Already clocked in."})
            elif action == 'out':
                if att.clock_out is None:
                    att.clock_out = now
                else:
                    return jsonify({"success": False, "msg": "Already clocked out."})
            db.session.commit()
            return jsonify({"success": True, "employee": emp.username, "action": action, "time": str(now)})
    return jsonify({"success": False, "msg": "Face not recognized."}), 404

# --- API: Get Attendance Logs for User (for frontend) ---

@app.route('/api/attendance', methods=['GET'])
def api_attendance():
    if 'user_id' not in session:
        return jsonify([])
    user = Employee.query.get(session['user_id'])
    if user.role == 'admin':
        records = Attendance.query.order_by(Attendance.date.desc()).all()
    elif user.role == 'manager':
        records = Attendance.query.join(Employee).filter(Employee.department==user.department).order_by(Attendance.date.desc()).all()
    else:
        records = Attendance.query.filter_by(employee_id=user.id).order_by(Attendance.date.desc()).all()
    result = []
    for r in records:
        result.append({
            "employee": r.employee.username,
            "date": str(r.date),
            "clock_in": str(r.clock_in) if r.clock_in else "",
            "clock_out": str(r.clock_out) if r.clock_out else "",
            "department": r.employee.department
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
