#!/usr/bin/env python
# coding: utf-8

# In[4]:


# app.py
import streamlit as st
import pandas as pd
import psycopg2
import streamlit.components.v1 as components

st.set_page_config(page_title="🚖 OLA Ride Insights", layout="wide")
st.title("🚖 OLA Ride Insights Dashboard")

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["📊 Power BI Dashboard", "🛠️ SQL Query Runner"])

with tab1:
    st.header("Power BI Dashboard")
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiYmFmMmEwZmMtNWQ2Ny00ZGMyLWE4ZTctMDEyNGJlMzI0M2ZkIiwidCI6ImM2OWZmZTY1LTY3ZDUtNGE1OC05MDA4LTBkMDljMDRkYmU2OCJ9"
    components.iframe(powerbi_url, width=1000, height=600, scrolling=True)

with tab2:
    st.header("Run Predefined / Custom SQL Queries")

    # --- Supabase connection using st.secrets ---
    def run_query(query: str):
        """Run a SQL query on Supabase and return a DataFrame."""
        if not query.strip().lower().startswith("select"):
            raise Exception("❌ Only SELECT queries are allowed for safety.")

        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASS"],
            port=st.secrets["DB_PORT"],
            sslmode="require",
            connect_timeout=10
        )
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        df = pd.DataFrame(rows, columns=cols)
        cur.close()
        conn.close()
        return df

    # --- Predefined queries ---
    queries = {
    "1. Retrieve all successful bookings":
        'SELECT * FROM cleaned_ola_dataset WHERE "Booking_Status" = \'Success\' LIMIT 50;',

    "2. Avg Ride Distance per Vehicle":
        'SELECT "Vehicle_Type", AVG("Ride_Distance"::numeric) AS avg_ride_by_vehicle FROM cleaned_ola_dataset GROUP BY "Vehicle_Type";',
,

    "3. Total cancelled rides by customers":
        'SELECT COUNT(*) AS total_rides_canceled_by_customer FROM cleaned_ola_dataset WHERE "Canceled_Rides_by_Customer" = \'Yes\';',

    "4. Top 5 customers by bookings":
        'SELECT "Customer_ID", COUNT("Booking_ID") AS total_booking_by_customer FROM cleaned_ola_dataset GROUP BY "Customer_ID" ORDER BY total_booking_by_customer DESC LIMIT 5;',

    "5. Driver cancellations for personal/car issues":
        'SELECT COUNT(*) AS cancel_with_reason FROM cleaned_ola_dataset WHERE "Canceled_Rides_by_Driver" = \'Personal & Car related issue\';',

    "6. Max & Min driver ratings for Prime Sedan":
        'SELECT MAX("Driver_Ratings") AS max_rating, MIN("Driver_Ratings") AS min_rating FROM cleaned_ola_dataset WHERE "Vehicle_Type" = \'Prime Sedan\';',

    "7. Rides paid using UPI":
        'SELECT * FROM cleaned_ola_dataset WHERE "Payment_Method" = \'UPI\' LIMIT 50;',

    "8. Avg customer rating per vehicle":
        'SELECT "Vehicle_Type", AVG("Customer_Rating") AS avg_rating_by_customer FROM cleaned_ola_dataset GROUP BY "Vehicle_Type";',

    "9. Total booking value of successful rides":
        'SELECT SUM("Booking_Value") AS total_booking_value FROM cleaned_ola_dataset WHERE "Booking_Status" = \'Success\';',

    "10. Incomplete rides + reason":
        'SELECT "Booking_Id", "Incomplete_Rides_Reason" FROM cleaned_ola_dataset WHERE "Incomplete_Rides" = \'Yes\';'


    }

    # --- UI controls ---
    choice = st.selectbox("📌 Choose a predefined query", list(queries.keys()))
    custom_sql = st.text_area("✍️ Or write a custom SQL query here (SELECT ...)", height=120)

    col1, col2 = st.columns(2)

    # Run predefined
    if col1.button("Run Selected Query"):
        try:
            df = run_query(queries[choice])
            st.success(f"✅ Query returned {len(df)} rows.")
            st.dataframe(df)
            if not df.empty and df.shape[1] > 1:
                try:
                    st.bar_chart(df.set_index(df.columns[0]))
                except Exception:
                    st.info("📊 Chart not suitable for this result.")
        except Exception as e:
            st.error(f"Error: {e}")

    # Run custom
    if col2.button("Run Custom Query"):
        if not custom_sql.strip():
            st.warning("⚠️ Please write a SELECT query first.")
        else:
            try:
                df = run_query(custom_sql)
                st.success(f"✅ Query returned {len(df)} rows.")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")

st.sidebar.info("⚠️ Note: Sometimes the database may auto-pause (Supabase free tier limitation). "
                "If a query doesn’t run immediately, please try 2–3 times and the output will appear. "
                "This is a cloud limitation, not an issue with the project.")




# In[ ]:




