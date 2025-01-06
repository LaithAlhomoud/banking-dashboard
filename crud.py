import streamlit as st
import pandas as pd
from database import engine, execute_sql
from sqlalchemy import text

# List of tables in the database
table_names = [
    'access', 'assist', 'bankaccount', 'branch', 'branchaddress', 'branchemail',
    'branchphone', 'customer', 'customeremail', 'customernationalid', 'customerphone',
    'employee', 'employeeemail', 'employeenationalid', 'employeephone',
    'fixedrateinvestment', 'loan', 'loantype', 'locker', 'lockerbranch',
    'lockercustomer', 'rolename', 'rolepermission', 'rolestatus', 'transaction',
    'variablerateinvestment'
]

def fetch_table_data(table_name):
    query = f"SELECT * FROM {table_name}"
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def display_crud_operations():
    st.sidebar.title("Tables")
    selected_table = st.sidebar.selectbox("Select a table to manage:", table_names)

    if selected_table:
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
