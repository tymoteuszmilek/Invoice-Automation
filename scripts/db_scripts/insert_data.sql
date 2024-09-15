-- Start a transaction
BEGIN;

DROP TABLE IF EXISTS temp_invoices;
-- Create Temp Table to hold data imported from CSV file
CREATE TEMP TABLE temp_invoices (
	invoice_number VARCHAR(50) UNIQUE NOT NULL,
	vendor_name VARCHAR(100) NOT NULL,
	address VARCHAR(100) NOT NULL,
	issued_date DATE NOT NULL,
    due_date DATE NOT NULL,
    invoice_status VARCHAR(50),
    product_name VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL 
);

\copy temp_invoices FROM '../../data/cleaned_invoices/customer_invoices_dataset.csv' DELIMITER ',' CSV HEADER;





-- Insert specific columns into Target Tables
INSERT INTO Vendors (vendor_name, address)
SELECT DISTINCT
    vendor_name, address
FROM
    temp_invoices;
    



-- Insert invoices into Invoices table, resolving vendor_id
WITH vendor_ids AS (
	SELECT
		vendor_id,
		vendor_name,
		address
	FROM
		Vendors
)
INSERT INTO Invoices (invoice_number, issued_date, due_date, vendor_id, invoice_status)
SELECT	
	t.invoice_number,
	t.issued_date,
	t.due_date,
	v.vendor_id,
	t.invoice_status
FROM
	temp_invoices t
JOIN
	vendor_ids v
ON
	t.vendor_name = v.vendor_name AND t.address = v.address;




-- Insert products into Products table
INSERT INTO Products (product_name, unit_price)
SELECT DISTINCT
	product_name, unit_price
FROM
	temp_invoices;
	



-- Insert invoice items into Invoice_Items table, resolving invoice_id and product_id
WITH invoice_ids AS (
    SELECT
        invoice_number,
        invoice_id
    FROM
        Invoices
),
product_ids AS (
    SELECT
        product_name,
        unit_price,
        product_id
    FROM
        Products
)
INSERT INTO Invoice_Items (invoice_id, product_id, quantity)
SELECT
    i.invoice_id,
    p.product_id,
    t.quantity
FROM
    temp_invoices t
JOIN
    invoice_ids i
ON
    t.invoice_number = i.invoice_number
JOIN
    product_ids p
ON
    t.product_name = p.product_name AND t.unit_price = p.unit_price;
	
DROP TABLE temp_invoices;

-- Commit the transaction
COMMIT;