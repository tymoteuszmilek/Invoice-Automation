-- Start a transaction
BEGIN;

DROP TABLE IF EXISTS Invoice_Items;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Invoices;
DROP TABLE IF EXISTS Vendors;

CREATE TABLE Vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL,
    company_name VARCHAR(50),
    contact_info TEXT
);

CREATE TABLE Invoices (
    invoice_id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    issued_date DATE NOT NULL,
    due_date DATE NOT NULL,
    vendor_id INTEGER REFERENCES Vendors(vendor_id),
    invoice_status VARCHAR(50)
);

CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    description TEXT,
    unit_price DECIMAL(10,2) NOT NULL 
);

CREATE TABLE Invoice_Items (
    item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES Invoices(invoice_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES Products(product_id),
    quantity INTEGER NOT NULL,
    line_total DECIMAL(10, 2)
);

-- Create the trigger function to update line_total based on quantity and unit_price
CREATE OR REPLACE FUNCTION update_line_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.line_total := NEW.quantity * (SELECT unit_price FROM Products WHERE product_id = NEW.product_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER calculate_line_total
BEFORE INSERT OR UPDATE ON Invoice_Items
FOR EACH ROW
EXECUTE FUNCTION update_line_total();

-- Commit the transaction
COMMIT;
