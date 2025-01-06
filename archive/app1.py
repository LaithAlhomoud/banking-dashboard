# Banking System Dashboard with CRUD and Visualizations
import pydeck as pdk
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
from streamlit_echarts import st_echarts  # For interactive charts
from geopy.geocoders import Nominatim      # For geocoding addresses
from geopy.extra.rate_limiter import RateLimiter
import time

# Initialize database connection
engine = create_engine("mysql+pymysql://root:asdzxc.62001@localhost/bankingsystem")

# List of tables in the database
table_names = [
    'access', 'assist', 'bankaccount', 'branch', 'branchaddress', 'branchemail',
    'branchphone', 'customer', 'customeremail', 'customernationalid', 'customerphone',
    'employee', 'employeeemail', 'employeenationalid', 'employeephone',
    'fixedrateinvestment', 'loan', 'loantype', 'locker', 'lockerbranch',
    'lockercustomer', 'rolename', 'rolepermission', 'rolestatus', 'transaction',
    'variablerateinvestment'
]

# Function to fetch table data
def fetch_table_data(table_name):
    query = f"SELECT * FROM {table_name}"
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

# Function to execute SQL commands for Create, Update, Delete
def execute_sql(query, params=None):
    try:
        with engine.connect() as conn:
            if params:
                conn.execute(text(query), params)
            else:
                conn.execute(text(query))
            conn.commit()  # Ensure the transaction is committed
            st.success("Operation completed successfully!")
    except Exception as e:
        st.error(f"Error executing query: {e}")

# Functions for Visualizations

def get_account_type_distribution():
    query = "SELECT Type, COUNT(*) as count FROM bankaccount GROUP BY Type"
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    types = data['Type'].tolist()
    counts = data['count'].tolist()
    return types, counts

def get_customer_ages():
    query = "SELECT DateOfBirth FROM customer"
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    today = pd.to_datetime('today').normalize()
    data['DateOfBirth'] = pd.to_datetime(data['DateOfBirth'])
    data['Age'] = data['DateOfBirth'].apply(
        lambda dob: today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    )
    ages = data['Age'].tolist()
    return ages

def get_customer_growth_over_time():
    query = """
    SELECT YEAR(SetupDate) as Year, COUNT(DISTINCT CustomerID) as CustomerCount
    FROM bankaccount
    GROUP BY Year
    ORDER BY Year
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_branch_assets():
    query = """
    SELECT b.Name, SUM(ba.Balance) as TotalBalance
    FROM bankaccount ba
    JOIN branch b ON ba.BranchID = b.BranchID
    GROUP BY b.Name 
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_loan_distribution_by_type():
    query = """
    SELECT l.Type, COUNT(*) as LoanCount, SUM(l.Amount) as TotalAmount
    FROM loan l
    GROUP BY l.Type
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_loan_status_breakdown():
    query = """
    SELECT Status, COUNT(*) as LoanCount
    FROM loan
    GROUP BY Status
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_transaction_volume_over_time():
    query = """
    SELECT DATE_FORMAT(Date, '%%Y-%%m') as Month, COUNT(*) as TransactionCount
    FROM `transaction`
    GROUP BY Month
    ORDER BY Month
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_branch_addresses():
    query = """
    SELECT ba.Street, ba.City, ba.State, ba.ZipCode, ba.Country,
           b.Name as BranchName
    FROM branchaddress ba
    JOIN branch b ON ba.BranchID = b.BranchID
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data


def geocode_addresses(addresses_df):
    geolocator = Nominatim(user_agent="branch_locator")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    addresses_df['FullAddress'] = (
        addresses_df['Street'] + ', ' +
        addresses_df['City'] + ', ' +
        addresses_df['State'] + ', ' +
        addresses_df['Country']
    )
    addresses_df['Location'] = addresses_df['FullAddress'].apply(geocode)
    addresses_df['Latitude'] = addresses_df['Location'].apply(lambda loc: loc.latitude if loc else None)
    addresses_df['Longitude'] = addresses_df['Location'].apply(lambda loc: loc.longitude if loc else None)
    addresses_df = addresses_df.dropna(subset=['Latitude', 'Longitude'])
    addresses_df = addresses_df.drop(columns=['Location'])
    return addresses_df



def plot_branch_locations():
    addresses_df = get_branch_addresses()
    addresses_df = geocode_addresses(addresses_df)
    if addresses_df.empty:
        st.warning("No branch locations available to display.")
    else:
        st.header("Branch Locations")
        # Define the tooltip
        tooltip = {
            "html": "<b>Branch Name:</b> {BranchName}<br/>"
                    "<b>Address:</b> {FullAddress}",
            "style": {"backgroundColor": "steelblue", "color": "white", "zIndex": "1000"}
        }
        # Create the layer with pickable=True
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=addresses_df,
            get_position='[Longitude, Latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=500,
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(
            latitude=addresses_df['Latitude'].mean(),
            longitude=addresses_df['Longitude'].mean(),
            zoom=6,
            pitch=0,
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(r)


def get_branch_locations():
    query = """
    SELECT ba.BranchID, b.Name, ba.Street, ba.City, ba.State, ba.ZipCode, ba.Country
    FROM branchaddress ba
    JOIN branch b ON ba.BranchID = b.BranchID
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def get_branch_locations_with_coordinates():
    data = get_branch_locations()
    geolocator = Nominatim(user_agent="bank_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    data['Address'] = data['Street'] + ', ' + data['City'] + ', ' + data['State'] + ', ' + data['Country']
    data['Coordinates'] = data['Address'].apply(geocode)
    data['Latitude'] = data['Coordinates'].apply(lambda loc: loc.latitude if loc else None)
    data['Longitude'] = data['Coordinates'].apply(lambda loc: loc.longitude if loc else None)
    # Remove entries without coordinates
    data = data.dropna(subset=['Latitude', 'Longitude'])
    return data

def get_investment_returns():
    # Query to get average ReturnRate over time from variablerateinvestment
    query_variable = """
    SELECT DATE_FORMAT(StartDate, '%%Y-%%m') as Period, AVG(ReturnRate) as AverageReturnRate
    FROM variablerateinvestment
    GROUP BY Period
    ORDER BY Period
    """
    # Query to get average InterestRate over time from fixedrateinvestment
    query_fixed = """
    SELECT DATE_FORMAT(StartDate, '%%Y-%%m') as Period, AVG(InterestRate) as AverageInterestRate
    FROM fixedrateinvestment
    GROUP BY Period
    ORDER BY Period
    """
    with engine.connect() as conn:
        data_variable = pd.read_sql(query_variable, conn)
        data_fixed = pd.read_sql(query_fixed, conn)
    # Merge the two datasets on Period
    data = pd.merge(data_variable, data_fixed, on='Period', how='outer').fillna(0)
    return data

def get_investment_portfolio():
    # Query to get total Amount from fixedrateinvestment
    query_fixed = """
    SELECT 'Fixed Rate Investment' as InvestmentType, SUM(Amount) as TotalAmount
    FROM fixedrateinvestment
    """
    # Query to get total Amount from variablerateinvestment
    query_variable = """
    SELECT 'Variable Rate Investment' as InvestmentType, SUM(Amount) as TotalAmount
    FROM variablerateinvestment
    """
    with engine.connect() as conn:
        data_fixed = pd.read_sql(query_fixed, conn)
        data_variable = pd.read_sql(query_variable, conn)
    # Combine the two datasets
    data = pd.concat([data_fixed, data_variable], ignore_index=True)
    return data

# Main Streamlit App
def main():
    st.title("Banking System Dashboard with CRUD and Visualizations")

    # Sidebar options for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["CRUD Operations", "Visualizations"])

    if page == "CRUD Operations":
        # Sidebar for table selection
        st.sidebar.title("Tables")
        selected_table = st.sidebar.selectbox("Select a table to manage:", table_names)

        if selected_table:
            # Display the table data
            st.header(f"Table: {selected_table}")
            try:
                data = fetch_table_data(selected_table)
                st.dataframe(data)

                # CRUD Options
                st.subheader("CRUD Operations")

                # Create Operation
                st.subheader("Create New Record")
                with st.form("create_form"):
                    inputs = {}
                    for column in data.columns:
                        value = st.text_input(f"Enter value for {column}")
                        if column == "DateOfBirth" and value:  # Validate date format
                            try:
                                pd.to_datetime(value)
                            except ValueError:
                                st.error(f"Invalid date format for {column}. Use YYYY-MM-DD.")
                        inputs[column] = value.strip()  # Strip whitespace

                    submit_create = st.form_submit_button("Create")
                    if submit_create:
                        if not all(inputs.values()):  # Ensure all fields are filled
                            st.error("All fields are required.")
                        else:
                            try:
                                # Prepare the INSERT query
                                columns = ", ".join(inputs.keys())
                                placeholders = ", ".join([f":{key}" for key in inputs.keys()])
                                query = f"INSERT INTO {selected_table} ({columns}) VALUES ({placeholders})"

                                # Execute the query
                                execute_sql(query, inputs)
                                st.success("Record added successfully!")
                            except Exception as e:
                                st.error(f"Error inserting record: {e}")

                # Update Operation
                st.subheader("Update Record")
                if not data.empty:
                    row_to_update = st.selectbox("Select a row to update:", data.index)
                    selected_row = data.loc[row_to_update]
                    with st.form("update_form"):
                        updates = {}
                        for column in data.columns:
                            value = st.text_input(f"Update {column}:", str(selected_row[column]))
                            updates[column] = value
                        submit_update = st.form_submit_button("Update")
                        if submit_update:
                            set_clause = ", ".join([f"{col} = :{col}" for col in updates.keys()])
                            query = f"UPDATE {selected_table} SET {set_clause} WHERE {data.columns[0]} = :id"
                            updates["id"] = selected_row[data.columns[0]]
                            execute_sql(query, updates)
                            st.success("Record updated successfully!")

                # Delete Operation
                st.subheader("Delete Record")
                if not data.empty:
                    row_to_delete = st.selectbox("Select a row to delete:", data.index)
                    selected_row = data.loc[row_to_delete]
                    delete_button = st.button("Delete")
                    if delete_button:
                        query = f"DELETE FROM {selected_table} WHERE {data.columns[0]} = :id"
                        execute_sql(query, {"id": selected_row[data.columns[0]]})
                        st.success("Record deleted successfully!")

            except Exception as e:
                st.error(f"Error: {e}")

    elif page == "Visualizations":
        # Sidebar for visualization selection
        st.sidebar.title("Visualizations")
        visualizations = [
            'Account Types Distribution',
            'Age Distribution',
            'Customer Growth Over Time',
            'Branch Assets Comparison',
            'Loan Distribution by Type',
            'Loan Status Breakdown',
            'Transaction Volume Over Time',
            'Geographical Distribution',
            'Investment Returns',  # New visualization
            'Investment Portfolio Composition'  # New visualization
        ]

        selected_visualization = st.sidebar.selectbox("Select a visualization:", visualizations)

        if selected_visualization == 'Account Types Distribution':
            st.header('Account Types Distribution')
            try:
                types, counts = get_account_type_distribution()
                # Prepare ECharts options
                pie_data = [{"value": count, "name": acc_type} for acc_type, count in zip(types, counts)]
                options = {
                    "title": {"text": "Account Types Distribution", "left": "center"},
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"},
                    "series": [
                        {
                            "name": "Account Types",
                            "type": "pie",
                            "radius": "50%",
                            "data": pie_data,
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                                }
                            },
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Age Distribution':
            st.header('Age Distribution')
            try:
                ages = get_customer_ages()
                age_counts = pd.Series(ages).value_counts().sort_index()
                options = {
                    "title": {"text": "Age Distribution of Customers", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": age_counts.index.tolist(), "name": "Age"},
                    "yAxis": {"type": "value", "name": "Number of Customers"},
                    "series": [
                        {
                            "data": age_counts.values.tolist(),
                            "type": "bar",
                            "barWidth": "60%",
                            "itemStyle": {"color": "#5470C6"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Customer Growth Over Time':
            st.header('Customer Growth Over Time')
            try:
                data = get_customer_growth_over_time()
                years = data['Year'].tolist()
                counts = data['CustomerCount'].tolist()
                options = {
                    "title": {"text": "Customer Growth Over Time", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": years, "name": "Year"},
                    "yAxis": {"type": "value", "name": "Number of New Customers"},
                    "series": [
                        {
                            "data": counts,
                            "type": "line",
                            "smooth": True,
                            "itemStyle": {"color": "#EE6666"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Branch Assets Comparison':
            st.header('Branch Assets Comparison')
            try:
                data = get_branch_assets()
                branch_names = data['Name'].tolist()
                total_balances = data['TotalBalance'].tolist()
                options = {
                    "title": {"text": "Total Assets by Branch", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": branch_names, "name": "Branch"},
                    "yAxis": {"type": "value", "name": "Total Balance"},
                    "series": [
                        {
                            "data": total_balances,
                            "type": "bar",
                            "barWidth": "60%",
                            "itemStyle": {"color": "#91CC75"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Loan Distribution by Type':
            st.header('Loan Distribution by Type')
            try:
                data = get_loan_distribution_by_type()
                loan_types = data['Type'].tolist()
                loan_counts = data['LoanCount'].tolist()
                options = {
                    "title": {"text": "Loan Distribution by Type", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": loan_types, "name": "Loan Type"},
                    "yAxis": {"type": "value", "name": "Number of Loans"},
                    "series": [
                        {
                            "data": loan_counts,
                            "type": "bar",
                            "barWidth": "60%",
                            "itemStyle": {"color": "#73C0DE"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Loan Status Breakdown':
            st.header('Loan Status Breakdown')
            try:
                data = get_loan_status_breakdown()
                statuses = data['Status'].tolist()
                loan_counts = data['LoanCount'].tolist()
                pie_data = [{"value": count, "name": status} for status, count in zip(statuses, loan_counts)]
                options = {
                    "title": {"text": "Loan Status Breakdown", "left": "center"},
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"},
                    "series": [
                        {
                            "name": "Loan Status",
                            "type": "pie",
                            "radius": "50%",
                            "data": pie_data,
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                                }
                            },
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Transaction Volume Over Time':
            st.header('Transaction Volume Over Time')
            try:
                data = get_transaction_volume_over_time()
                if data.empty:
                    st.warning("No data available for transaction volume over time.")
                else:
                    dates = data['Month'].tolist()
                    counts = data['TransactionCount'].tolist()
                    options = {
                        "title": {"text": "Transaction Volume Over Time", "left": "center"},
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": dates, "name": "Month"},
                        "yAxis": {"type": "value", "name": "Number of Transactions"},
                        "series": [
                            {
                                "data": counts,
                                "type": "line",
                                "smooth": True,
                                "areaStyle": {},  # Optional for area chart
                                "itemStyle": {"color": "#5470C6"},
                            }
                        ],
                    }
                    st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")


        elif selected_visualization == 'Geographical Distribution':
            st.header('Geographical Distribution')
            try:
                plot_branch_locations()
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Investment Returns':
            st.header('Investment Returns')
            try:
                data = get_investment_returns()
                periods = data['Period'].tolist()
                avg_return_rates = data['AverageReturnRate'].tolist()
                avg_interest_rates = data['AverageInterestRate'].tolist()
                options = {
                    "title": {"text": "Average Investment Returns Over Time", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["Average Return Rate", "Average Interest Rate"], "top": "bottom"},
                    "xAxis": {"type": "category", "data": periods, "name": "Period"},
                    "yAxis": {"type": "value", "name": "Rate (%)"},
                    "series": [
                        {
                            "name": "Average Return Rate",
                            "data": avg_return_rates,
                            "type": "line",
                            "smooth": True,
                            "itemStyle": {"color": "#5470C6"},
                        },
                        {
                            "name": "Average Interest Rate",
                            "data": avg_interest_rates,
                            "type": "line",
                            "smooth": True,
                            "itemStyle": {"color": "#91CC75"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")

        elif selected_visualization == 'Investment Portfolio Composition':
            st.header('Investment Portfolio Composition')
            try:
                data = get_investment_portfolio()
                investment_types = data['InvestmentType'].tolist()
                total_amounts = data['TotalAmount'].tolist()
                options = {
                    "title": {"text": "Investment Portfolio Composition", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": investment_types, "top": "bottom"},
                    "xAxis": {"type": "category", "data": investment_types, "name": "Investment Type"},
                    "yAxis": {"type": "value", "name": "Total Amount"},
                    "series": [
                        {
                            "name": "Total Amount",
                            "data": total_amounts,
                            "type": "bar",
                            "stack": "Total",
                            "itemStyle": {"color": "#5470C6"},
                        }
                    ],
                }
                st_echarts(options=options, height="500px")
            except Exception as e:
                st.error(f"Error generating visualization: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Banking System Dashboard", page_icon="🏦")
    main()
