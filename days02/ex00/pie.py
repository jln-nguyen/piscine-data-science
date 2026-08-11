import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

load_dotenv()
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PW")
db = os.getenv("POSTGRES_DB")

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@localhost:5432/{db}')

try:
    connection = engine.connect()
    print("Connection to PostgreSQL established successfully!")
except Exception as e:
    print(f"Connection failed! Error: {e}")

query = "SELECT event_type, COUNT(*) AS total FROM customers GROUP BY event_type;"

df = pd.read_sql(query, connection)
print(df)
plt.pie(df["total"], labels=df["event_type"], autopct="%1.1f%%")
plt.show()