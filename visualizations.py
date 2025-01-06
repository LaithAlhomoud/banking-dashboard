import streamlit as st
from geopy import Nominatim
from streamlit_echarts import st_echarts
import pandas as pd
from database import engine
from geocoding import plot_branch_locations  # If needed
from geopy.extra.rate_limiter import RateLimiter

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

def display_visualizations():
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [
                    {
                        "name": "Account Types",
                        "type": "pie",
                        "radius": "75%",
                        "data": pie_data,
                        "label": {
                            "show": True,
                            "textStyle": {
                                "fontSize": 18,  # Adjust this value
                                "color": "#000000"
                            }
                        },
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
        st.header('Age Distribution of Customers')
        try:
            ages = get_customer_ages()
            age_counts = pd.Series(ages).value_counts().sort_index()
            options = {
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": age_counts.index.tolist(), "name": "Age", "axisLabel": {"fontSize": 13, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "Number of Customers", "axisLabel": {"fontSize": 13, "color": "#000000"}},
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": years, "name": "Year", "axisLabel": {"fontSize": 13, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "New Customers", "axisLabel": {"fontSize": 13, "color": "#000000"}},
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": branch_names, "name": "Branch","axisLabel": {"fontSize": 10, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "Total Balance","axisLabel": {"fontSize": 13, "color": "#000000"}},
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": loan_types, "name": "Loan Type","axisLabel": {"fontSize": 13, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "Number of Loans","axisLabel": {"fontSize": 13, "color": "#000000"}},
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [
                    {
                        "name": "Loan Status",
                        "type": "pie",
                        "radius": "75%",
                        "label": {
                            "show": True,
                            "textStyle": {
                                "fontSize": 18,  # Adjust this value
                                "color": "#000000"
                            }
                        },
                        "data": pie_data,
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.0)",
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
                    "title": {"text": "", "left": "center"},
                    "backgroundColor": "rgba(255, 255, 255, 0.8)",
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": dates, "name": "Month","axisLabel": {"fontSize": 13, "color": "#000000"}},
                    "yAxis": {"type": "value", "name": "Number of Transactions","axisLabel": {"fontSize": 13, "color": "#000000"}},
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
        st.header('Average Investment Returns Over Time')
        try:
            data = get_investment_returns()
            periods = data['Period'].tolist()
            avg_return_rates = data['AverageReturnRate'].tolist()
            avg_interest_rates = data['AverageInterestRate'].tolist()
            options = {
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Average Return Rate", "Average Interest Rate"], "top": "bottom"},
                "xAxis": {"type": "category", "data": periods, "name": "Period","axisLabel": {"fontSize": 13, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "Rate (%)","axisLabel": {"fontSize": 13, "color": "#000000"}},
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
                "title": {"text": "", "left": "center"},
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "tooltip": {"trigger": "axis"},
                "legend": {"data": investment_types, "top": "bottom"},
                "xAxis": {"type": "category", "data": investment_types, "name": "Investment Type", "axisLabel": {"fontSize": 13, "color": "#000000"}},
                "yAxis": {"type": "value", "name": "Total Amount", "axisLabel": {"fontSize": 13, "color": "#000000"}},
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
