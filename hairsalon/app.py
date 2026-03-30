"""
Glamour Hair Salon – Flask backend
Run:  python app.py
"""

import os
import logging
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, query_db, execute_db, rows_to_list, row_to_dict
from notifications import (
    notify_appointment_created,
    notify_appointment_cancelled,
    notify_appointment_reminder,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _appt_full(appt_id: int) -> dict | None:
    """Return appointment joined with customer, staff, service."""
    row = query_db(
        """
        SELECT a.*,
               c.name  AS customer_name, c.email AS customer_email, c.phone AS customer_phone,
               s.name  AS staff_name,
               sv.name AS service_name, sv.price AS price, sv.duration_minutes AS duration_minutes
        FROM appointments a
        JOIN customers c  ON c.id  = a.customer_id
        JOIN staff     s  ON s.id  = a.staff_id
        JOIN services  sv ON sv.id = a.service_id
        WHERE a.id = ?
        """,
        (appt_id,),
        one=True,
    )
    return row_to_dict(row)


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route('/api/dashboard/stats')
def dashboard_stats():
    from datetime import date
    today = date.today().isoformat()

    total_today = query_db(
        "SELECT COUNT(*) as c FROM appointments WHERE appointment_date = ?", (today,), one=True
    )['c']

    revenue_today = query_db(
        """
        SELECT COALESCE(SUM(sv.price), 0) as r
        FROM appointments a
        JOIN services sv ON sv.id = a.service_id
        WHERE a.appointment_date = ? AND a.status IN ('confirmed','completed')
        """,
        (today,),
        one=True,
    )['r']

    total_customers = query_db("SELECT COUNT(*) as c FROM customers", one=True)['c']
    active_staff    = query_db("SELECT COUNT(*) as c FROM staff WHERE active = 1", one=True)['c']

    upcoming = rows_to_list(query_db(
        """
        SELECT a.id, a.appointment_date, a.appointment_time, a.status,
               c.name AS customer_name, sv.name AS service_name, s.name AS staff_name
        FROM appointments a
        JOIN customers c  ON c.id  = a.customer_id
        JOIN staff     s  ON s.id  = a.staff_id
        JOIN services  sv ON sv.id = a.service_id
        WHERE a.appointment_date >= ? AND a.status NOT IN ('cancelled','completed')
        ORDER BY a.appointment_date, a.appointment_time
        LIMIT 10
        """,
        (today,),
    ))

    return jsonify({
        'total_today':      total_today,
        'revenue_today':    round(revenue_today, 2),
        'total_customers':  total_customers,
        'active_staff':     active_staff,
        'upcoming':         upcoming,
    })


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

@app.route('/api/appointments', methods=['GET'])
def list_appointments():
    date_filter   = request.args.get('date')
    status_filter = request.args.get('status')
    search        = request.args.get('search', '').strip()

    sql = """
        SELECT a.id, a.appointment_date, a.appointment_time, a.status,
               a.notes, a.email_sent, a.sms_sent, a.created_at,
               c.name AS customer_name, c.phone AS customer_phone, c.email AS customer_email,
               s.name AS staff_name,
               sv.name AS service_name, sv.price AS price, sv.duration_minutes AS duration_minutes,
               a.customer_id, a.staff_id, a.service_id
        FROM appointments a
        JOIN customers c  ON c.id  = a.customer_id
        JOIN staff     s  ON s.id  = a.staff_id
        JOIN services  sv ON sv.id = a.service_id
        WHERE 1=1
    """
    args = []
    if date_filter:
        sql += " AND a.appointment_date = ?"
        args.append(date_filter)
    if status_filter:
        sql += " AND a.status = ?"
        args.append(status_filter)
    if search:
        sql += " AND (c.name LIKE ? OR sv.name LIKE ? OR s.name LIKE ?)"
        like = f'%{search}%'
        args.extend([like, like, like])

    sql += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
    return jsonify(rows_to_list(query_db(sql, args)))


@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json(force=True)
    required = ('customer_id', 'staff_id', 'service_id', 'appointment_date', 'appointment_time')
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'Missing required fields'}), 400

    appt_id = execute_db(
        """
        INSERT INTO appointments (customer_id, staff_id, service_id, appointment_date,
                                  appointment_time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data['customer_id'], data['staff_id'], data['service_id'],
            data['appointment_date'], data['appointment_time'],
            data.get('status', 'scheduled'),
            data.get('notes', ''),
        ),
    )

    appt = _appt_full(appt_id)
    if appt:
        result = notify_appointment_created(appt)
        execute_db(
            "UPDATE appointments SET email_sent = ?, sms_sent = ? WHERE id = ?",
            (int(result['email']), int(result['sms']), appt_id),
        )
        appt['email_sent'] = int(result['email'])
        appt['sms_sent']   = int(result['sms'])

    return jsonify(appt), 201


@app.route('/api/appointments/<int:appt_id>', methods=['GET'])
def get_appointment(appt_id):
    appt = _appt_full(appt_id)
    if not appt:
        abort(404)
    return jsonify(appt)


@app.route('/api/appointments/<int:appt_id>', methods=['PUT'])
def update_appointment(appt_id):
    old = _appt_full(appt_id)
    if not old:
        abort(404)

    data = request.get_json(force=True)
    fields = ('customer_id', 'staff_id', 'service_id', 'appointment_date',
              'appointment_time', 'status', 'notes')
    updates = {f: data[f] for f in fields if f in data}
    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    set_clause = ', '.join(f'{k} = ?' for k in updates)
    execute_db(
        f'UPDATE appointments SET {set_clause} WHERE id = ?',
        list(updates.values()) + [appt_id],
    )

    appt = _appt_full(appt_id)

    # Fire cancellation notification when status flips to cancelled
    new_status = updates.get('status', old.get('status'))
    if new_status == 'cancelled' and old.get('status') != 'cancelled':
        result = notify_appointment_cancelled(appt)
        execute_db(
            "UPDATE appointments SET email_sent = ?, sms_sent = ? WHERE id = ?",
            (int(result['email']), int(result['sms']), appt_id),
        )

    return jsonify(_appt_full(appt_id))


@app.route('/api/appointments/<int:appt_id>', methods=['DELETE'])
def delete_appointment(appt_id):
    appt = _appt_full(appt_id)
    if not appt:
        abort(404)
    execute_db('DELETE FROM appointments WHERE id = ?', (appt_id,))
    return jsonify({'deleted': appt_id})


@app.route('/api/appointments/<int:appt_id>/remind', methods=['POST'])
def send_reminder(appt_id):
    appt = _appt_full(appt_id)
    if not appt:
        abort(404)
    result = notify_appointment_reminder(appt)
    return jsonify({'sms': result['sms'], 'email': result['email']})


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

@app.route('/api/services', methods=['GET'])
def list_services():
    return jsonify(rows_to_list(query_db(
        "SELECT * FROM services ORDER BY name"
    )))


@app.route('/api/services', methods=['POST'])
def create_service():
    data = request.get_json(force=True)
    if not all(data.get(f) for f in ('name', 'duration_minutes', 'price')):
        return jsonify({'error': 'Missing required fields'}), 400
    sid = execute_db(
        "INSERT INTO services (name, description, duration_minutes, price) VALUES (?,?,?,?)",
        (data['name'], data.get('description', ''), int(data['duration_minutes']), float(data['price'])),
    )
    return jsonify(row_to_dict(query_db("SELECT * FROM services WHERE id=?", (sid,), one=True))), 201


@app.route('/api/services/<int:sid>', methods=['PUT'])
def update_service(sid):
    if not query_db("SELECT id FROM services WHERE id=?", (sid,), one=True):
        abort(404)
    data = request.get_json(force=True)
    fields = ('name', 'description', 'duration_minutes', 'price')
    updates = {f: data[f] for f in fields if f in data}
    if not updates:
        return jsonify({'error': 'No fields to update'}), 400
    set_clause = ', '.join(f'{k} = ?' for k in updates)
    execute_db(f'UPDATE services SET {set_clause} WHERE id = ?', list(updates.values()) + [sid])
    return jsonify(row_to_dict(query_db("SELECT * FROM services WHERE id=?", (sid,), one=True)))


@app.route('/api/services/<int:sid>', methods=['DELETE'])
def delete_service(sid):
    if not query_db("SELECT id FROM services WHERE id=?", (sid,), one=True):
        abort(404)
    execute_db("DELETE FROM services WHERE id=?", (sid,))
    return jsonify({'deleted': sid})


# ---------------------------------------------------------------------------
# Staff
# ---------------------------------------------------------------------------

@app.route('/api/staff', methods=['GET'])
def list_staff():
    return jsonify(rows_to_list(query_db("SELECT * FROM staff ORDER BY name")))


@app.route('/api/staff', methods=['POST'])
def create_staff():
    data = request.get_json(force=True)
    if not all(data.get(f) for f in ('name', 'role')):
        return jsonify({'error': 'Missing required fields'}), 400
    sid = execute_db(
        "INSERT INTO staff (name, role, email, phone, active) VALUES (?,?,?,?,?)",
        (data['name'], data['role'], data.get('email',''), data.get('phone',''), 1),
    )
    return jsonify(row_to_dict(query_db("SELECT * FROM staff WHERE id=?", (sid,), one=True))), 201


@app.route('/api/staff/<int:sid>', methods=['PUT'])
def update_staff(sid):
    if not query_db("SELECT id FROM staff WHERE id=?", (sid,), one=True):
        abort(404)
    data = request.get_json(force=True)
    fields = ('name', 'role', 'email', 'phone', 'active')
    updates = {f: data[f] for f in fields if f in data}
    if not updates:
        return jsonify({'error': 'No fields to update'}), 400
    set_clause = ', '.join(f'{k} = ?' for k in updates)
    execute_db(f'UPDATE staff SET {set_clause} WHERE id = ?', list(updates.values()) + [sid])
    return jsonify(row_to_dict(query_db("SELECT * FROM staff WHERE id=?", (sid,), one=True)))


@app.route('/api/staff/<int:sid>', methods=['DELETE'])
def delete_staff(sid):
    if not query_db("SELECT id FROM staff WHERE id=?", (sid,), one=True):
        abort(404)
    execute_db("DELETE FROM staff WHERE id=?", (sid,))
    return jsonify({'deleted': sid})


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@app.route('/api/customers', methods=['GET'])
def list_customers():
    search = request.args.get('search', '').strip()
    if search:
        like = f'%{search}%'
        rows = query_db(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? ORDER BY name",
            (like, like, like),
        )
    else:
        rows = query_db("SELECT * FROM customers ORDER BY name")
    return jsonify(rows_to_list(rows))


@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json(force=True)
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    cid = execute_db(
        "INSERT INTO customers (name, email, phone) VALUES (?,?,?)",
        (data['name'], data.get('email',''), data.get('phone','')),
    )
    return jsonify(row_to_dict(query_db("SELECT * FROM customers WHERE id=?", (cid,), one=True))), 201


@app.route('/api/customers/<int:cid>', methods=['GET'])
def get_customer(cid):
    customer = row_to_dict(query_db("SELECT * FROM customers WHERE id=?", (cid,), one=True))
    if not customer:
        abort(404)
    history = rows_to_list(query_db(
        """
        SELECT a.id, a.appointment_date, a.appointment_time, a.status,
               sv.name AS service_name, sv.price, s.name AS staff_name
        FROM appointments a
        JOIN services sv ON sv.id = a.service_id
        JOIN staff s     ON s.id  = a.staff_id
        WHERE a.customer_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (cid,),
    ))
    customer['appointments'] = history
    return jsonify(customer)


@app.route('/api/customers/<int:cid>', methods=['PUT'])
def update_customer(cid):
    if not query_db("SELECT id FROM customers WHERE id=?", (cid,), one=True):
        abort(404)
    data = request.get_json(force=True)
    fields = ('name', 'email', 'phone')
    updates = {f: data[f] for f in fields if f in data}
    if not updates:
        return jsonify({'error': 'No fields to update'}), 400
    set_clause = ', '.join(f'{k} = ?' for k in updates)
    execute_db(f'UPDATE customers SET {set_clause} WHERE id = ?', list(updates.values()) + [cid])
    return jsonify(row_to_dict(query_db("SELECT * FROM customers WHERE id=?", (cid,), one=True)))


@app.route('/api/customers/<int:cid>', methods=['DELETE'])
def delete_customer(cid):
    if not query_db("SELECT id FROM customers WHERE id=?", (cid,), one=True):
        abort(404)
    execute_db("DELETE FROM customers WHERE id=?", (cid,))
    return jsonify({'deleted': cid})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
