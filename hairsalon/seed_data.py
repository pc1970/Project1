"""
Seed the database with sample data.
Run:  python seed_data.py
"""

from database import init_db, execute_db, query_db

def seed():
    init_db()

    # Staff
    staff = [
        ('Sophia Martinez', 'Senior Stylist',   'sophia@glamourhair.com',  '(555) 201-0001'),
        ('James Rivera',    'Colorist',          'james@glamourhair.com',   '(555) 201-0002'),
        ('Ava Thompson',    'Junior Stylist',    'ava@glamourhair.com',     '(555) 201-0003'),
    ]
    staff_ids = []
    for name, role, email, phone in staff:
        existing = query_db("SELECT id FROM staff WHERE email=?", (email,), one=True)
        if existing:
            staff_ids.append(existing['id'])
        else:
            sid = execute_db(
                "INSERT INTO staff (name, role, email, phone, active) VALUES (?,?,?,?,1)",
                (name, role, email, phone),
            )
            staff_ids.append(sid)

    # Services
    services = [
        ('Women\'s Haircut',        'Precision cut, wash & blow-dry',              45,  65.00),
        ('Men\'s Haircut',          'Classic cut, wash & style',                   30,  40.00),
        ('Full Color',              'Single process all-over color',               90, 120.00),
        ('Highlights',              'Partial or full foil highlights',            120, 150.00),
        ('Balayage',                'Hand-painted sun-kissed highlights',         150, 180.00),
        ('Keratin Treatment',       'Smoothing treatment for frizz-free hair',    120, 200.00),
        ('Deep Conditioning',       'Intensive moisture treatment',                30,  45.00),
        ('Blowout & Style',         'Shampoo, blow-dry & style',                   45,  55.00),
    ]
    service_ids = []
    for name, desc, dur, price in services:
        existing = query_db("SELECT id FROM services WHERE name=?", (name,), one=True)
        if existing:
            service_ids.append(existing['id'])
        else:
            sid = execute_db(
                "INSERT INTO services (name, description, duration_minutes, price) VALUES (?,?,?,?)",
                (name, desc, dur, price),
            )
            service_ids.append(sid)

    # Customers
    customers = [
        ('Emily Chen',      'emily.chen@email.com',      '(555) 301-0001'),
        ('Michael Brown',   'mbrown@email.com',          '(555) 301-0002'),
        ('Olivia Davis',    'olivia.d@email.com',        '(555) 301-0003'),
        ('Liam Wilson',     'lwilson@email.com',         '(555) 301-0004'),
        ('Isabella Garcia', 'igarccia@email.com',        '(555) 301-0005'),
        ('Noah Martinez',   'nmartinez@email.com',       '(555) 301-0006'),
        ('Mia Anderson',    'mia.anderson@email.com',    '(555) 301-0007'),
        ('Ethan Taylor',    'ethan.t@email.com',         '(555) 301-0008'),
        ('Ava Thomas',      'ava.thomas@email.com',      '(555) 301-0009'),
        ('William Lee',     'will.lee@email.com',        '(555) 301-0010'),
    ]
    customer_ids = []
    for name, email, phone in customers:
        existing = query_db("SELECT id FROM customers WHERE email=?", (email,), one=True)
        if existing:
            customer_ids.append(existing['id'])
        else:
            cid = execute_db(
                "INSERT INTO customers (name, email, phone) VALUES (?,?,?)",
                (name, email, phone),
            )
            customer_ids.append(cid)

    # Appointments  (spread across past / today / future)
    from datetime import date, timedelta
    today = date.today()

    appts = [
        # past – completed
        (customer_ids[0], staff_ids[0], service_ids[0], (today - timedelta(days=7)).isoformat(), '10:00', 'completed'),
        (customer_ids[1], staff_ids[1], service_ids[2], (today - timedelta(days=5)).isoformat(), '14:00', 'completed'),
        (customer_ids[2], staff_ids[2], service_ids[7], (today - timedelta(days=3)).isoformat(), '11:30', 'completed'),
        (customer_ids[3], staff_ids[0], service_ids[1], (today - timedelta(days=2)).isoformat(), '09:00', 'completed'),
        # today
        (customer_ids[4], staff_ids[1], service_ids[4], today.isoformat(),                       '10:00', 'confirmed'),
        (customer_ids[5], staff_ids[2], service_ids[0], today.isoformat(),                       '13:00', 'confirmed'),
        (customer_ids[6], staff_ids[0], service_ids[3], today.isoformat(),                       '15:30', 'scheduled'),
        # upcoming
        (customer_ids[7], staff_ids[1], service_ids[5], (today + timedelta(days=1)).isoformat(), '11:00', 'scheduled'),
        (customer_ids[8], staff_ids[0], service_ids[6], (today + timedelta(days=2)).isoformat(), '14:00', 'scheduled'),
        (customer_ids[9], staff_ids[2], service_ids[0], (today + timedelta(days=3)).isoformat(), '09:30', 'scheduled'),
        (customer_ids[0], staff_ids[1], service_ids[2], (today + timedelta(days=4)).isoformat(), '12:00', 'scheduled'),
        (customer_ids[1], staff_ids[0], service_ids[7], (today + timedelta(days=5)).isoformat(), '16:00', 'scheduled'),
        # cancelled
        (customer_ids[2], staff_ids[2], service_ids[1], (today + timedelta(days=1)).isoformat(), '10:00', 'cancelled'),
        (customer_ids[3], staff_ids[1], service_ids[3], (today - timedelta(days=1)).isoformat(), '15:00', 'cancelled'),
        (customer_ids[4], staff_ids[0], service_ids[4], (today + timedelta(days=6)).isoformat(), '11:30', 'scheduled'),
    ]

    existing_count = query_db("SELECT COUNT(*) as c FROM appointments", one=True)['c']
    if existing_count == 0:
        for cust, stf, svc, dt, tm, status in appts:
            execute_db(
                """INSERT INTO appointments
                   (customer_id, staff_id, service_id, appointment_date, appointment_time, status)
                   VALUES (?,?,?,?,?,?)""",
                (cust, stf, svc, dt, tm, status),
            )

    print('Seed data inserted successfully.')


if __name__ == '__main__':
    seed()
