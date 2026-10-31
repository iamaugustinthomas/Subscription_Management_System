# Subscription Management System for Brightloop Software

This repository contains the backend infrastructure for a unified subscription management platform, specifically engineered to serve as the digital backbone for Brightloop Software.

Built with Python (Flask) and SQLAlchemy, this system replaces Brightloop's legacy manual processes such as spreadsheets, manual invoice generation, and bank matching with an automated, scalable, and secure architecture.

## Development Team

This enterprise solution was architected and developed by:

* Augustin Thomas
* Allen Francis
* Akhil Mohan
* Jacob Ninan Raju

## Proposed Solution and Value Proposition

This platform systematically resolves the operational challenges outlined in Brightloop's current workflow:

* **Unified Portal Architecture:** Customers authenticate securely (enforced by strict cryptographic password policies requiring a minimum of eight characters, mixed casing, and special characters) into a dedicated portal to manage their subscriptions independently, thereby reducing administrative overhead.
* **Role Based Access Control (RBAC):** The system enforces strict authorization parameters. Administrators maintain comprehensive system oversight, including discount configuration and staff provisioning. Internal Staff are granted scoped access for daily operations, while Customers are restricted to their proprietary data.
* **Automated Billing and Renewals:** The system eliminates manual invoicing. A scheduled chron ready process automatically calculates taxes and generates draft invoices on billing cycles based on active subscription data. The subscription lifecycle is rigorously tracked through distinct states: Draft, Quotation, Confirmed, Active, and Closed.
* **Dynamic Product and Plan Catalogs:** The architecture natively supports Brightloop's diverse catalog, accommodating base products, tier variants (e.g., Odoo brand markups), and flexible billing intervals (daily, weekly, monthly, yearly) alongside automated contract lifecycles.
* **Algorithmic Discount Engine:** Administrators can deploy fixed or percentage based discounts governed by strict parameters (temporal limits, maximum utilization thresholds, and minimum seat quantities). These variables are automatically reconciled and applied to subsequent invoices without manual intervention.
* **Real Time Financial Reporting:** End of quarter manual reporting is superseded by automated analytics. The financial dashboard endpoint delivers sub two second query resolution for critical metrics, including active subscription counts, gross revenue, collected payments, and outstanding accounts receivable.

## Prerequisites and Setup

* Python 3.8+
* pip (Python package installer)

### Installation Procedure

1. **Clone the repository:**
   Ensure `app.py` is present in your designated working directory.

2. **Initialize a virtual environment (Recommended):**

   ```bash
   python  m venv venv
   source venv/bin/activate  # Windows environments: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install Flask Flask SQLAlchemy Werkzeug
   ```

4. **Execute the application:**

   ```bash
   python app.py
   ```

   *Note: Upon initial execution, the application automatically provisions a local SQLite database (`brightloop.db`) and deploys the optimized relational schema.*

## Core API Endpoints

This platform exposes a RESTful API designed for seamless integration with Brightloop's client portal and internal operational dashboards.

### Authentication and User Management

* **`POST /api/auth/register`**
  * *Function:* Secure customer onboarding and credential validation. Enforces unique email constraints and complex security protocols.

* **`POST /api/admin/staff`**
  * *Function:* Administrator exclusive endpoint to provision authenticated accounts for internal operational personnel.

### Billing and Automation

* **`POST /api/billing/generate`**
  * *Function:* Automated billing execution. Scans all active subscriptions to programmatically generate draft invoices, calculate precise tax obligations, and categorically prevent duplicate billing instances.

### Financial Analytics

* **`GET /api/finance/dashboard`**
  * *Function:* Executive financial overview. Returns an optimized, low latency JSON payload detailing:
    * `active_subscriptions`
    * `total_revenue`
    * `collected_payments`
    * `overdue_invoices`

## Database Architecture

To guarantee query performance under two seconds at scale, the relational database is normalized into the following domain models:

* **Authentication:** `user`
* **Catalog Management:** `product`, `product_variant`
* **Contract Terms:** `plan`, `discount_rule`
* **Service Agreements:** `subscription`, `subscription_line`
* **Accounts Receivable:** `invoice`, `payment`