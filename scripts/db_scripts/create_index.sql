BEGIN;

CREATE INDEX idx_vendor_name ON Vendors (vendor_name);

CREATE INDEX idx_issued_date ON Invoices (issued_date);
CREATE INDEX idx_due_date ON Invoices (due_date);
CREATE INDEX idx_invoice_status ON Invoices (invoice_status);

CREATE INDEX idx_product_name ON Products (product_name);

CREATE INDEX idx_invoice_id ON Invoice_Items (invoice_id);
CREATE INDEX idx_product_id ON Invoice_Items (product_id);

COMMIT;