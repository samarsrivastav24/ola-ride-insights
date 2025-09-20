#!/usr/bin/env python
# coding: utf-8

# In[8]:


import streamlit as st
import pandas as pd
import mysql.connector
import streamlit.components.v1 as components

st.set_page_config(page_title="OLA Ride Insights", layout="wide")

st.title("🚖 OLA Ride Insights Dashboard")

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["📊 Power BI Dashboard", "🛠️ SQL Query Runner"])

# ---------------- Power BI Tab ----------------
with tab1:
    st.header("Power BI Dashboard")
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiYmFmMmEwZmMtNWQ2Ny00ZGMyLWE4ZTctMDEyNGJlMzI0M2ZkIiwidCI6ImM2OWZmZTY1LTY3ZDUtNGE1OC05MDA4LTBkMDljMDRkYmU2OCJ9"
    components.iframe(powerbi_url, width=1000, height=600, scrolling=True)

# ---------------- SQL Query Runner Tab ----------------
with tab2:
    st.header("Run Predefined SQL Queries")

    # Sidebar: DB connection
    st.sidebar.header("Database Connection")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", type="password")
    database = st.sidebar.text_input("Database", "ola_project")

    # Predefined SQL queries
    queries = {
        "1. Retrieve all successful bookings":
            """SELECT * 
               FROM cleaned_ola_dataset 
               WHERE Booking_Status = "Success";""",

        "2. Find the average ride distance for each vehicle type":
            """SELECT Vehicle_Type,
                      AVG(Ride_Distance) AS avg_ride_by_vehicle
               FROM cleaned_ola_dataset
               GROUP BY Vehicle_Type;""",

        "3. Get the total number of cancelled rides by customers":
            """SELECT COUNT(canceled_Rides_by_Customer) AS total_rides_canceled_by_customer
               FROM cleaned_ola_dataset;""",

        "4. List the top 5 customers who booked the highest number of rides":
            """SELECT Customer_ID, COUNT(Booking_ID) AS total_booking_by_customer
               FROM cleaned_ola_dataset
               GROUP BY Customer_ID
               ORDER BY total_booking_by_customer DESC
               LIMIT 5;""",

        "5. Get the number of rides cancelled by drivers due to personal and car-related issues":
            """SELECT COUNT(Canceled_Rides_by_Driver) AS cancel_with_reason
               FROM cleaned_ola_dataset
               WHERE Canceled_Rides_by_Driver = "Personal & Car related issue";""",

        "6. Find the maximum and minimum driver ratings for Prime Sedan bookings":
            """SELECT Vehicle_Type,
                      MAX(Driver_Ratings) AS max_rating,
                      MIN(Driver_Ratings) AS min_rating
               FROM cleaned_ola_dataset
               WHERE Vehicle_Type = "Prime Sedan";""",

        "7. Retrieve all rides where payment was made using UPI":
            """SELECT * 
               FROM cleaned_ola_dataset
               WHERE Payment_Method = "UPI";""",

        "8. Find the average customer rating per vehicle type":
            """SELECT Vehicle_Type,
                      AVG(Customer_Rating) AS avg_rating_by_customer
               FROM cleaned_ola_dataset
               GROUP BY Vehicle_Type;""",

        "9. Calculate the total booking value of rides completed successfully":
            """SELECT SUM(Booking_Value) AS total_booking_value
               FROM cleaned_ola_dataset
               WHERE Booking_Status = "Success";""",

        "10. List all incomplete rides along with the reason":
            """SELECT Booking_Id, Incomplete_Rides_Reason
               FROM cleaned_ola_dataset
               WHERE Incomplete_Rides = "Yes";"""
    }

    # Dropdown for queries
    choice = st.selectbox("📌 Choose a query to run", list(queries.keys()))

    if st.button("Run Query"):
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            cursor.execute(queries[choice])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            df = pd.DataFrame(rows, columns=columns)
            st.subheader(f"Results for: {choice}")
            st.dataframe(df)

            if not df.empty and df.shape[1] > 1:
                try:
                    st.bar_chart(df.set_index(df.columns[0]))
                except Exception:
                    st.info("📊 Chart not suitable for this query.")

            cursor.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error: {e}")


# In[ ]:




