from sqlalchemy import create_engine, text
from config import DATABASE_URI

# Initialize database connection
engine = create_engine(DATABASE_URI)

def execute_sql(query, params=None):
    try:
        with engine.connect() as conn:
            if params:
                conn.execute(text(query), params)
            else:
                conn.execute(text(query))
            conn.commit()
    except Exception as e:
        raise e
