# 🏦 Banking System Dashboard with CRUD and Visualizations

Welcome to the **Banking System Dashboard**, your serene gateway to managing and visualizing banking data effortlessly. This application is designed to provide a smooth and intuitive experience, ensuring that handling complex banking operations feels as calming as a gentle breeze.

---

## 🌟 Features

- **Comprehensive CRUD Operations**  
  Easily create, read, update, and delete records across various banking tables with a user-friendly interface.

- **Interactive Visualizations**  
  Gain insights through beautifully crafted charts and maps, including:
  - **Investment Returns**: Track average Return Rates and Interest Rates over time with elegant line charts.
  - **Investment Portfolio Composition**: Compare Fixed and Variable Rate Investments by Amount using soothing stacked bar charts.
  - And much more: Explore a variety of visualizations to understand your banking data deeply.

- **Geographical Mapping**  
  Visualize branch locations on an interactive map, enhancing your spatial understanding of your banking network.

- **Modular Architecture**  
  Experience seamless navigation and maintainability with a thoughtfully organized codebase.

---

## 🛠️ Technologies Used

- **Streamlit**: For building the interactive web application interface.
- **SQLAlchemy**: Facilitating smooth ORM-based interactions with the MySQL database.
- **PyDeck & Geopy**: Empowering geospatial visualizations and geocoding functionalities.
- **ECharts via Streamlit-ECharts**: Creating dynamic and responsive charts for insightful data representation.
- **Pandas**: Managing and manipulating data with ease.

---

## 📂 Project Structure

The project embraces a modular design, organized into distinct files for clarity:

```plaintext
banking-system-dashboard/
├── app.py
├── database.py
├── crud.py
├── visualizations.py
├── geocoding.py
├── config.py
├── utils.py
├── README.md
└── requirements.txt
```

## 🔍 Detailed Overview

### **app.py**  
- **Function**: The heart of the application, orchestrating navigation and integrating all components.  
- **Key Function**: `main()`

### **database.py**  
- **Function**: Manages the serene connection to the MySQL database and facilitates SQL query executions.  
- **Key Function**: `execute_sql(query, params=None)`

### **crud.py**  
- **Function**: Handles all Create, Read, Update, and Delete operations, ensuring smooth data management.  
- **Key Functions**:
  - `fetch_table_data(table_name)`
  - `display_crud_operations()`

### **visualizations.py**  
- **Function**: Curates and presents insightful visualizations, transforming data into clear, calming visuals.  
- **Key Functions**:
  - **Data Retrieval**:
    - `get_account_type_distribution()`
    - `get_customer_ages()`
    - `get_customer_growth_over_time()`
    - `get_branch_assets()`
    - `get_loan_distribution_by_type()`
    - `get_loan_status_breakdown()`
    - `get_transaction_volume_over_time()`
    - `get_investment_returns()`
    - `get_investment_portfolio()`
  - **Visualization Display**:
    - `display_visualizations()`

### **geocoding.py**  
- **Function**: Brings branch data to life with geocoding and mapping, offering a peaceful spatial perspective.  
- **Key Functions**:
  - `get_branch_locations()`
  - `geocode_addresses(addresses_df)`
  - `plot_branch_locations()`

### **config.py**  
- **Function**: Safeguards your configuration settings, including sensitive database connection strings.  
- **Key Variable**: `DATABASE_URI`

## 🎨 Usage

### **CRUD Operations**
1. Select the **CRUD Operations** page from the sidebar.
2. Choose a table to manage from the dropdown.
   - **Create**: Add new records effortlessly using the provided form.
   - **Read**: View existing records in a clean, organized table.
   - **Update**: Modify records with ease through the update form.
   - **Delete**: Remove unwanted records seamlessly with a simple click.

### **Visualizations**
1. Navigate to the **Visualizations** page via the sidebar.
2. Select from a variety of visualizations to gain insights into your banking data:
   - **Investment Returns**: Observe the harmonious trends of Return Rates and Interest Rates over time.
   - **Investment Portfolio Composition**: Compare and contrast Fixed and Variable Rate Investments by their amounts.
   - **And more**: Explore additional visualizations to deepen your understanding.

### **Geographical Mapping**
1. View the serene distribution of your bank branches on an interactive map.
2. Hover over branch locations to reveal detailed information in a calm and clear tooltip.

## 📞 Contact

For any inquiries or support, feel free to reach out:

- **Email**: [Laith.alhomoud@aurak.ac.ae](mailto:Laith.alhomoud@aurak.ac.ae)  
- **GitHub**: [LaithAlhomoud](https://github.com/LaithAlhomoud)  

