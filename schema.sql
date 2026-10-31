-- Schema for Brightloop Software Subscription Management System

-- Users and Roles
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('admin', 'staff', 'customer')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    sales_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Variants
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value VARCHAR(100) NOT NULL,
    price_extra DECIMAL(10, 2) DEFAULT 0.00
);

-- Plans
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    billing_frequency VARCHAR(50) CHECK (billing_frequency IN ('daily', 'weekly', 'monthly', 'yearly')) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    min_quantity INT DEFAULT 1,
    available_from DATE,
    available_to DATE,
    auto_close BOOLEAN DEFAULT FALSE,
    closable_early BOOLEAN DEFAULT TRUE,
    pauseable BOOLEAN DEFAULT TRUE,
    renewable BOOLEAN DEFAULT TRUE
);

-- Taxes
CREATE TABLE taxes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rate DECIMAL(5, 4) NOT NULL,
    rules TEXT
);

-- Discounts
CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    discount_type VARCHAR(50) CHECK (discount_type IN ('fixed', 'percentage')) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    min_purchase DECIMAL(10, 2),
    min_quantity INT,
    start_date DATE,
    end_date DATE,
    usage_limit INT,
    product_id INT REFERENCES products(id), -- NULL if applies to whole subscription
    created_by INT REFERENCES users(id) -- must be admin
);

-- Quotation Templates
CREATE TABLE quotation_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan_id INT REFERENCES plans(id),
    validity_days INT NOT NULL
);

-- Quotation Template Lines
CREATE TABLE quotation_template_lines (
    id SERIAL PRIMARY KEY,
    template_id INT REFERENCES quotation_templates(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT DEFAULT 1
);

-- Subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    subscription_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id INT REFERENCES users(id) NOT NULL,
    plan_id INT REFERENCES plans(id) NOT NULL,
    start_date DATE NOT NULL,
    expiry_date DATE,
    payment_terms TEXT,
    status VARCHAR(50) CHECK (status IN ('Draft', 'Quotation', 'Confirmed', 'Active', 'Closed')) DEFAULT 'Draft'
);

-- Subscription Lines
CREATE TABLE subscription_lines (
    id SERIAL PRIMARY KEY,
    subscription_id INT REFERENCES subscriptions(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id) NOT NULL,
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    tax_id INT REFERENCES taxes(id),
    amount DECIMAL(10, 2) NOT NULL
);

-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    subscription_id INT REFERENCES subscriptions(id),
    customer_id INT REFERENCES users(id) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_total DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('Draft', 'Confirmed', 'Paid')) DEFAULT 'Draft'
);

-- Invoice Lines
CREATE TABLE invoice_lines (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);

-- Payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,
    method VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    notes TEXT
);
