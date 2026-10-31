from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import re
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
DB_FILE = "brightloop.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name', 'Brightloop Franchise Client')

    if not email or not password:
        return jsonify({"error": "Missing profile credentials."}), 400

    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{9,}$"
    if not re.match(password_regex, password):
        return jsonify({"error": "Security Alert: Password does not fulfill complexity requirements."}), 400

    conn = get_db_connection()
    try:
        user_id = conn.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'customer')",
                               (email, password)).lastrowid
        conn.execute("INSERT INTO customers (user_id, company_name) VALUES (?, ?)", (user_id, company_name))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Conflict: Account identity identifier already exists."}), 409
    finally:
        conn.close()
    return jsonify({"message": "Subscriber record created successfully."}), 201

@app.route('/api/admin/add-staff', methods=['POST'])
def add_staff():
    requesting_role = request.headers.get('X-User-Role')
    if requesting_role != 'admin':
        return jsonify({"error": "Unauthorized Access Denied: Action restricted to Administrators."}), 403
    
    data = request.json
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'staff')", 
                     (data['email'], data['password']))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email is already assigned to a team member."}), 409
    finally:
        conn.close()
    return jsonify({"message": "Internal team member successfully provisioned."}), 201

@app.route('/api/billing/run-cycle', methods=['POST'])
def run_billing_cycle():
    conn = get_db_connection()
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    billable_subs = conn.execute("""
        SELECT s.*, p.sales_price, p.id as prod_id, pv.price_modifier, c.id as cust_id 
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        LEFT JOIN product_variants pv ON s.variant_id = pv.id
        JOIN customers c ON s.customer_id = c.id
        WHERE s.status = 'Active' 
          AND s.id NOT IN (SELECT subscription_id FROM invoices WHERE billing_period_start = ?)
    """, (today_str,)).fetchall()

    invoices_created = 0
    for sub in billable_subs:
        base_unit_rate = sub['sales_price'] + (sub['price_modifier'] if sub['price_modifier'] else 0.0)
        subtotal = base_unit_rate * sub['quantity']
        
        discount = conn.execute("""
            SELECT * FROM discount_rules 
            WHERE (target_product_id = ? OR target_product_id IS NULL)
              AND start_date <= ? AND (end_date >= ? OR end_date IS NULL)
              AND (usage_limit IS NULL OR times_used < usage_limit)
              AND min_quantity <= ?
            ORDER BY value DESC LIMIT 1
        """, (sub['prod_id'], today_str, today_str, sub['quantity'])).fetchone()

        discount_amount = 0.0
        if discount:
            if discount['discount_type'] == 'percentage':
                discount_amount = subtotal * (discount['value'] / 100.0)
            else:
                discount_amount = discount['value']
            conn.execute("UPDATE discount_rules SET times_used = times_used + 1 WHERE id = ?", (discount['id'],))

        tax_amount = (subtotal - discount_amount) * sub['tax_rate']
        total = (subtotal - discount_amount) + tax_amount
        
        invoice_number = f"INV-{sub['subscription_number']}-{datetime.today().strftime('%M%S%f')[:8]}"
        due_date = (datetime.today() + timedelta(days=15)).strftime('%Y-%m-%d')

        conn.execute("""
            INSERT INTO invoices (subscription_id, customer_id, invoice_number, subtotal, tax_amount, discount_amount, total, status, due_date, billing_period_start)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?, ?)
        """, (sub['id'], sub['cust_id'], invoice_number, subtotal, tax_amount, discount_amount, total, due_date, today_str))
        invoices_created += 1

    conn.commit()
    conn.close()
    return jsonify({"status": "Batch processing success", "invoices_generated": invoices_created}), 200

@app.route('/api/finance/dashboard', methods=['GET'])
def get_dashboard_metrics():
    conn = get_db_connection()
    
    metrics = conn.execute("""
        SELECT 
            (SELECT COUNT(*) FROM subscriptions WHERE status = 'Active') as active_subscriptions,
            (SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status = 'Paid') as total_revenue,
            (SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status != 'Paid') as total_outstanding,
            (SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status != 'Paid' AND due_date < date('now')) as total_overdue
        """).fetchone()

    overdue_list = conn.execute("""
        SELECT i.invoice_number, c.company_name, i.total, i.due_date 
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.status != 'Paid' AND i.due_date < date('now')
        ORDER BY i.due_date ASC
    """).fetchall()

    response = {
        "summary": dict(metrics),
        "overdue_invoices": [dict(row) for row in overdue_list]
    }
    conn.close()
    return jsonify(response), 200

if __name__ == '__main__':
    import os
    if not os.path.exists(DB_FILE):
        with open("schema.sql", "r") as f:
            conn = sqlite3.connect(DB_FILE)
            conn.executescript(f.read())
            conn.commit()
            conn.close()
    app.run(port=5000, debug=True)
