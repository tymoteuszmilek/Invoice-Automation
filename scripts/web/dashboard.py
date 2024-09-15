from dash import dcc, html, Input, Output, dash_table
from dash.dependencies import State
import pandas as pd
import dash
from sqlalchemy import create_engine
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import dash_bootstrap_components as dbc


def get_engine():
    user = os.getenv('DB_USER', 'default_user')  
    password = os.getenv('DB_PASSWORD', 'default_password')  
    host = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_NAME', 'new')
    return create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{database}')


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    html.H1("Invoice Dashboard", style={'text-align': 'center', 'margin-bottom': '30px', 'margin-top': '30px'}),

    # Container for filters
    html.Div([
        # Search field
        html.Div([
            html.Label('Search: ', style={'font-size': '18px', 'margin-right': '10px'}),
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='vendor_name / invoice_number',
                style={
                    'width': '300px',
                    'height': '35px',
                    'font-size': '18px',
                    'padding': '5px',
                    'border-radius': '5px',
                    'border': '1px solid #ccc'
                }
            ),
        ], style={'margin-bottom': '15px', 'display': 'flex', 'align-items': 'center'}),

        # Date pickers (Start and End Date)
        html.Div([
            # Start Date Picker
            html.Div([
                html.Label('Start Date: ', style={'font-size': '18px', 'margin-right': '5px'}),
                dcc.DatePickerSingle(
                    id='start-date-picker',
                    date='2022-07-10',
                    style={
                        'width': '180px',
                        'height': '35px',
                        'font-size': '16px',
                        'padding': '5px',
                        'border-radius': '5px',
                        'border': '1px solid #ccc'
                    }
                ),
            ], style={'margin-bottom': '10px', 'display': 'flex', 'align-items': 'center', 'margin-right': '20px'}),

            # End Date Picker
            html.Div([
                html.Label('End Date: ', style={'font-size': '18px', 'margin-right': '5px'}),
                dcc.DatePickerSingle(
                    id='end-date-picker',
                    date='2023-08-08',
                    style={
                        'width': '180px',
                        'height': '35px',
                        'font-size': '16px',
                        'padding': '5px',
                        'border-radius': '5px',
                        'border': '1px solid #ccc'
                    }
                ),
            ], style={'margin-bottom': '10px', 'display': 'flex', 'align-items': 'center'}),
        ], style={'display': 'flex', 'margin-bottom': '20px'}),  # Flex row for date pickers

        # Invoice status dropdown
        html.Div([
            html.Label('Filter by Invoice Status: ', style={'font-size': '18px', 'margin-right': '10px'}),
            dcc.Dropdown(
                id='status-dropdown',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Pending', 'value': 'Pending'},
                    {'label': 'Overdue', 'value': 'Overdue'},
                    {'label': 'Paid', 'value': 'Paid'}
                ],
                value='All',  # Default value
                multi=False,
                style={
                    'width': '200px',
                    'font-size': '16px',
                    'padding': '5px',
                    'border-radius': '5px',
                    'border': '1px solid #ccc'
                }
            ),
        ], style={'margin-bottom': '20px', 'display': 'flex', 'align-items': 'center'}),
    ], style={
        'border': '1px solid #ddd', 'padding': '20px', 'border-radius': '10px',
        'box-shadow': '0 2px 10px rgba(0, 0, 0, 0.1)', 'max-width': '800px', 'margin': 'auto'
    }),

    html.Div([
        # Table container
        html.Div(
            dash_table.DataTable(
                id='invoice-table',
                columns=[{'name': col, 'id': col} for col in
                         ['invoice_number', 'vendor_name', 'line_total', 'invoice_status', 'issued_date', 'due_date']],
                data=[],  # Data will be populated via callback
                style_table={'height': '300px', 'overflowY': 'auto'},
                row_selectable='single',  # Allow single row selection
                selected_rows=[],  # No rows selected by default
            ),
            style={'margin-top': '30px','margin-bottom': '30px','margin-left': 'auto', 'margin-right': 'auto', 'width': '90%','border': '1px solid #ddd','padding': '20px', 'border-radius': '10px','box-shadow': '0 2px 10px rgba(0, 0, 0, 0.1)'}  # Centering and setting table width
        ),

        # Details section
        html.Div(id='details', style={'margin-top': '30px', 'max-width': '800px', 'margin': 'auto'}),

        # Container for alerts-buttons
        html.Div([
            # Container for alerts
            html.Div([
                dbc.Alert(
                    id='export-status',
                    children='',
                    color='success',
                    is_open=False,
                    style={
                        'margin-bottom': '20px',
                        'font-size': '16px',
                        'font-weight': 'bold'
                    }
                ),
                dbc.Alert(
                    id='report-status',
                    children='',
                    color='success',
                    is_open=False,
                    style={
                        'margin-bottom': '20px',
                        'font-size': '16px',
                        'font-weight': 'bold'
                    }
                ),
            ], style={'margin-bottom': '20px'}),

            # Container for the buttons
            html.Div([
                # Button for exporting to CSV
                html.Button(
                    'Export to CSV',
                    id='export-button',
                    style={
                        'padding': '10px 20px',
                        'font-size': '16px',
                        'background-color': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '5px',
                        'cursor': 'pointer',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto'
                    }
                ),
                # Button for creating reports
                html.Button('Generate Report', id='report-button', style={
                    'margin-top': '20px',
                    'padding': '10px 20px',
                    'font-size': '16px',
                    'background-color': '#28a745',
                    'color': 'white',
                    'border': 'none',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'display': 'block',
                    'margin-left': 'auto',
                    'margin-right': 'auto'
                })

            ], style={'text-align': 'center', 'margin-top': '20px'})
        ], style={'margin-top': '30px', 'margin-bottom': '30px'}),
])])


@app.callback(
    Output('invoice-table', 'data'),
    [Input('status-dropdown', 'value'),
     Input('search-input', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def update_table(status, search, start_date, end_date):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = """
            SELECT i.invoice_number, v.vendor_name, ii.line_total, i.invoice_status, i.issued_date,i.due_date
            FROM invoices i
            JOIN vendors v ON i.vendor_id = v.vendor_id
            JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
            WHERE (%s = 'All' OR i.invoice_status = %s)
            AND (i.invoice_number ILIKE %s OR v.vendor_name ILIKE %s)
            AND i.due_date BETWEEN %s AND %s
            """
            params = (status, status, f'%{search}%', f'%{search}%', start_date, end_date) # Tuple of parameters that will replace placeholders %s
            df = pd.read_sql(query, conn, params=params)
            return df.to_dict('records') # Convert to list of dicts in order to update table
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


@app.callback(
    Output('details', 'children'),
    [Input('invoice-table', 'selected_rows')],
    [State('invoice-table', 'data')]
)
def display_details(selected_rows, data):
    if selected_rows:
        selected_row = selected_rows[0]
        if selected_row < len(data):
            selected_invoice = data[selected_row]

            # Fetch more detail about invoice from database
            try:
                engine = get_engine()
                with engine.connect() as conn:
                    query = """
                    SELECT i.invoice_number, v.vendor_name, v.address, i.invoice_status, i.issued_date,i.due_date, p.product_name, ii.line_total
                    FROM invoices i
                    JOIN vendors v ON i.vendor_id = v.vendor_id
                    JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
                    JOIN products p ON ii.product_id = p.product_id
                    WHERE i.invoice_number = %s
                    """
                    invoice_number = selected_invoice['invoice_number']
                    details_df = pd.read_sql(query, conn, params=(invoice_number,))

                    # Fetching the first row of the result
                    if not details_df.empty:
                        details = details_df.iloc[0]

                        return html.Div([
                            html.H3(f"Details for Invoice {details['invoice_number']}"),
                            html.P(f"Vendor: {details['vendor_name']}"),
                            html.P(f"Vendor address: {details['address']}"),
                            html.P(f"Status: {details['invoice_status']}"),
                            html.P(f"Issued Date: {details['issued_date']}"),
                            html.P(f"Due Date: {details['due_date']}"),
                            html.P(f"Service: {details['product_name']}"),
                            html.P(f"Total amount: {details['line_total']}")

                        ])
                    else:
                        return html.Div([html.P("No additional details found for this invoice.")])
            except Exception as e:
                print(f"An error occurred: {e}")
                return html.Div([html.P(f"Error loading details: {e}")])

    return html.Div([html.P("No invoice selected.")])


@app.callback(
    [Output('export-status', 'children'),
     Output('export-status', 'color'),
     Output('export-status', 'is_open')],
    [Input('export-button', 'n_clicks')],
    [State('invoice-table', 'data'),
     State('start-date-picker', 'date'),
     State('end-date-picker', 'date'),
     State('status-dropdown', 'value')]
)
def export_to_csv(n_clicks, data, start_date, end_date, status):
    if n_clicks:
        try:
            df = pd.DataFrame(data)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            export_dir = os.path.join(script_dir, '../../data/CSVexports')
            os.makedirs(export_dir, exist_ok=True)  # Ensure the directory exists

            # Format the dates and status for the filename
            start_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y_%m_%d')
            end_date_str = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y_%m_%d')

            # Generate the dynamic filename
            file_name = f"{start_date_str}-{end_date_str}-{status}.csv"
            file_path = os.path.join(export_dir, file_name)

            df.to_csv(file_path, index=False)
            print(f"Exported data to {file_path}")

            return [f"Exported data to {file_path}", 'success', True]
        except Exception as e:
            print(f"An error occurred: {e}")
            return [f"An error occurred: {e}", 'danger', True]

    return ['', 'success', False]  # Default empty state when no clicks have occurred


def generate_reports(df, start_date, end_date, status):
    # Convert date columns to datetime
    df['issued_date'] = pd.to_datetime(df['issued_date'])
    df['due_date'] = pd.to_datetime(df['due_date'])

    # Filter data based on the selected status and date range
    if status != 'All':
        df = df[df['invoice_status'] == status]
    df = df[(df['issued_date'] >= start_date) & (df['issued_date'] <= end_date)]

    # Fetch more detail about invoice from database
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = """
                SELECT
                    SUM(ii.line_total) AS total_spending,
                    p.product_name AS product_name
                FROM
                    invoices i
                JOIN
                    invoice_items ii ON i.invoice_id = ii.invoice_id
                JOIN
                    products p ON ii.product_id = p.product_id
                WHERE
                    i.issued_date BETWEEN %s AND %s
                GROUP BY
                    p.product_name;
            """
            params = (start_date, end_date)
            df_cat = pd.read_sql(query, conn, params=params)
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Spending by Category (Product Name)
    plt.figure(figsize=(10, 6))
    if not df_cat.empty:
        df_cat.plot(kind='bar', x='product_name', y='total_spending', color='skyblue')
        plt.title('Total Spending by Category')
        plt.xlabel('Category')
        plt.ylabel('Total Spending')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('spending_by_category.png')
        plt.close()
    else:
        print("No data available for spending by category.")

    # Total Spending by Invoice Status
    df['invoice_status'] = df['invoice_status'].astype('category')
    status_totals = df.groupby('invoice_status', observed=False)['line_total'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(status_totals['invoice_status'], status_totals['line_total'], color=['skyblue', 'coral', 'gold'])
    plt.title('Total Spending by Invoice Status')
    plt.xlabel('Invoice Status')
    plt.ylabel('Total Spending')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('total_spending_by_status.png')
    plt.close()

    # Spending per Day
    daily_spending_df = df.set_index('issued_date')
    plt.figure(figsize=(10, 6))
    daily_spending_df.resample('D')['line_total'].sum().plot(kind='line', color='green')
    plt.title('Daily Spending')
    plt.xlabel('Date')
    plt.ylabel('Total Spending')
    plt.tight_layout()
    plt.savefig('daily_spending.png')
    plt.close()


@app.callback(
    [Output('report-status', 'children'),
     Output('report-status', 'color'),
     Output('report-status', 'is_open')],
    [Input('report-button', 'n_clicks')],
    [State('invoice-table', 'data'),
     State('start-date-picker', 'date'),
     State('end-date-picker', 'date'),
     State('status-dropdown', 'value')]
)
def generate_report(n_clicks, data, start_date, end_date, status):
    if n_clicks:
        if data and start_date and end_date and status:
            try:

                df = pd.DataFrame(data)

                script_dir = os.path.dirname(os.path.abspath(__file__))
                export_dir = os.path.join(script_dir, '../../data/Reports')
                os.makedirs(export_dir, exist_ok=True)

                # Format the dates and status for the filename
                start_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y_%m_%d')
                end_date_str = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y_%m_%d')
                file_prefix = f"{start_date_str}-{end_date_str}-{status}"

                # Generate and save reports
                generate_reports(df, start_date, end_date, status)

                # Move saved reports to the export directory
                report_files = ['spending_by_category.png', 'total_spending_by_status.png', 'daily_spending.png']
                for report in report_files:
                    report_path = os.path.join(script_dir, report)
                    if os.path.exists(report_path):
                        new_report_path = os.path.join(export_dir, f"{file_prefix}_{report}")
                        os.rename(report_path, new_report_path)
                        print(f"Exported data to {new_report_path}")

                return [f"Reports have been successfully generated and saved to {export_dir}!", 'success', True]

            except Exception as e:
                print(f"An error occurred: {e}")
                return [f"An error occurred: {e}", 'danger', True]
        else:
            return ["Please ensure all inputs are provided.", 'warning', True]

    return ['', 'success', False]  # Default empty state when no clicks have occurred


if __name__ == '__main__':
    app.run_server(debug=True)
