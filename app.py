from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)
migration = Migrate(application, db)

INVOICE_DIR = Path('static/bill')
INVOICE_DIR.mkdir(parents=True, exist_ok=True)

class InvoiceRecord(db.Model):
    __tablename__ = 'invoice_records'
    record_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

global_client_counter = 0

@application.route('/')
def landing_page():
    return render_template('index.html')

@application.route('/dashboard')
def admin_panel():
    generated_files = []
    if INVOICE_DIR.exists():
        for file_path in INVOICE_DIR.iterdir():
            if file_path.is_file():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                generated_files.append((mod_time, file_path.name))
                
    return render_template('Dashboard.html', bills=generated_files)

@application.route('/generate_bill', methods=['GET', 'POST'])
def create_invoice():
    global global_client_counter
    
    if request.method == 'POST':
        client = request.form.get('name')
        addr = request.form.get('address')
        tax_rate = request.form.get('gst_percent')
        item_count = int(request.form.get('total_items', 0))
        
        purchases = []
        for idx in range(1, item_count + 1):
            i_name = request.form.get(f'item_name_{idx}')
            i_price = request.form.get(f'item_price_{idx}')
            if i_name and i_price:
                purchases.append(f"  - {i_name}: {i_price}")
        
        global_client_counter += 1
        
        file_name = f"bill_{client}_{global_client_counter}.txt"
        target_path = INVOICE_DIR / file_name
        
        receipt_content = (
            "Brightloop Software\n\n"
            f"Customer ID: {global_client_counter}\n"
            f"Name: {client}\n"
            f"Address: {addr}\n"
            f"GST Percentage: {tax_rate}\n"
            "Items:\n" + "\n".join(purchases) + "\n"
        )
        
        target_path.write_text(receipt_content)
        
        return redirect(url_for('admin_panel'))

    return render_template('index.html')

if __name__ == '__main__':
    application.run(debug=True)