import pandas as pd
import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define input and output folders
input_folder = os.path.join(script_dir, '../../data/raw_invoices')
output_folder = os.path.join(script_dir, '../../data/cleaned_invoices')

# Create output folder if it doesn't already exist
os.makedirs(output_folder, exist_ok=True)

def clean_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    df.drop_duplicates(inplace=True)
    df.fillna('', inplace=True)
    
    if file_path.endswith('customer_invoices_dataset.csv'):
    	# Change the value of rows in id_invoice
    	df['id_invoice'] = df['id_invoice'].astype(str) + '-' + df['issuedDate'].astype(str) + '-' + df['client'].str[:2]

    	df.drop_duplicates(subset='id_invoice', keep='first', inplace=True)

   	 	# Dropping columns
    	columns_to_keep = ['id_invoice', 'issuedDate', 'country', 'service', 'total', 'invoiceStatus', 'dueDate', 'client']
    	df = df[columns_to_keep]

    	# Renaming columns
    	df.rename(columns={
        	'id_invoice': 'invoice_number',
        	'issuedDate': 'issued_date',
        	'total': 'unit_price',
        	'invoiceStatus': 'invoice_status',
        	'dueDate': 'due_date',
        	'client': 'vendor_name',
        	'country': 'address',
        	'service': 'product_name'
    	}, inplace=True)
    
    	# Add the quantity column with a value of 1 for each row
    	df['quantity'] = 1
    
    	# Setting column order
    	column_order = ['invoice_number', 'vendor_name', 'address', 'issued_date', 'due_date', 'invoice_status', 'product_name', 'quantity', 'unit_price']
    	df = df[column_order]

    return df

# Process each CSV file in the input_folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        input_file_path = os.path.join(input_folder, file_name)
        cleaned_data = clean_data(input_file_path)

        # Save cleaned data to output_folder
        output_file_path = os.path.join(output_folder, file_name)
        cleaned_data.to_csv(output_file_path, index=False)
        print(f"Processed {file_name} and saved to cleaned_invoices.")
