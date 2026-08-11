import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import matplotlib.dates as mdates
import numpy as np

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

query = """
    SELECT
        DATE(event_time) AS day,
        COUNT(DISTINCT user_id) as nb
    FROM customers
    WHERE event_type='purchase'
        AND event_time >= '2022-10-01'
        AND event_time < '2023-03-01'
    GROUP BY DATE(event_time)
    ORDER BY day;
"""

df1 = pd.read_sql(query, connection)
# print(df1)

fig, axes = plt.subplots(3, 1, figsize=(10, 12))

axes[0].plot(df1["day"], df1["nb"])
axes[0].set_ylabel("Number of Customers")

ax0 = axes[0]
ax0.spines["top"].set_visible(False)
ax0.spines["right"].set_visible(False)
ax0.spines["left"].set_visible(False)
ax0.spines["bottom"].set_visible(False)
ax0.tick_params(left=False, bottom=False)
ax0.xaxis.set_major_locator(mdates.MonthLocator())
ax0.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax0.set_xlim(df1["day"].min(), df1["day"].max())
ax0.set_ylim(bottom=0)
ax0.set_facecolor("lightgrey")
ax0.grid(c="white")
ax0.set_axisbelow(True)

# plt.show()

query2 = """
    SELECT
        DATE_TRUNC('month', event_time) AS month,
        SUM(price) as sales
    FROM customers
    WHERE event_type='purchase'
        AND event_time >= '2022-10-01'
        AND event_time < '2023-03-01'
    GROUP BY DATE_TRUNC('month', event_time)
    ORDER BY month;
"""
df2 = pd.read_sql(query2, connection)
# print(df2)
df2["sales_millions"] = df2["sales"] / 1000000
axes[1].bar(df2["month"].dt.strftime("%b"), df2["sales_millions"])
axes[1].set_ylabel("Total sales in million of ₳")
axes[1].set_xlabel("month")
ax1 = axes[1]
ax1.set_yticks(np.arange(0, df2["sales_millions"].max(), 0.2))
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_visible(False)
ax1.spines["bottom"].set_visible(False)
ax1.tick_params(left=False, bottom=False)
ax1.set_facecolor("lightgrey")
ax1.grid(axis = 'y', c="white")
ax1.set_axisbelow(True)

query3 = """
    SELECT
        DATE(event_time) AS day,
        SUM(price) / COUNT(DISTINCT user_id) AS avg_spend_per_customer
    FROM customers
    WHERE event_type = 'purchase'
      AND event_time >= '2022-10-01'
      AND event_time < '2023-03-01'
    GROUP BY DATE(event_time)
    ORDER BY day;
"""

df3 = pd.read_sql(query3, connection)
axes[2].stackplot(df3["day"], df3["avg_spend_per_customer"])
axes[2].set_ylabel("average spend/customer in ₳")

ax2 = axes[2]
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.tick_params(left=False, bottom=False)
ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax2.set_xlim(df1["day"].min(), df1["day"].max())
ax2.set_ylim(bottom=0)
ax2.set_facecolor("lightgrey")
ax2.grid(c="white")
ax2.set_axisbelow(True)

plt.show()