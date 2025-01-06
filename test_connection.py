from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("mysql+pymysql://root:asdzxc.62001@localhost/bankingsystem")

def fetch_table_names():
    query = """
    SELECT TABLE_NAME
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = 'bankingsystem';
    """
    with engine.connect() as conn:
        result = pd.read_sql(query, conn)
    return result['TABLE_NAME'].tolist()

table_names = fetch_table_names()
print(table_names)
