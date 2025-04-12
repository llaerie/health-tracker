# ----- LOGIN SETUP -----
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Hardcoded password (you can change this or read from secrets)
PASSWORD = "hellospring44"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    with st.form("login_form"):
        pwd = st.text_input("Enter password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if pwd == PASSWORD:
                st.session_state.authenticated = True
            else:
                st.error("Incorrect password!")

if not st.session_state.authenticated:
    st.title("Health Habit Tracker")
    login()
    st.stop()  # stops the rest of the app from running unless logged in

# Title
st.title("Health Habit Tracker")

# Input form
with st.form("habit_form"):
    sleep = st.number_input("Hours of Sleep", min_value=0.0, max_value=24.0, step=0.5)
    mood = st.slider("Mood (1–10)", 1, 10)
    exercise = st.checkbox("Exercised Today?")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Save Entry")

# Save data
if submitted:
    new_entry = pd.DataFrame({
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Sleep": [sleep],
        "Mood": [mood],
        "Exercise": ["Yes" if exercise else "No"],
        "Notes": [notes]
    })

    try:
        df = pd.read_csv("habit_data.csv")
        df = pd.concat([df, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry

    df.to_csv("habit_data.csv", index=False)
    st.success("Entry saved!")

# Load data
try:
    df = pd.read_csv("habit_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
except:
    df = pd.DataFrame()

# Visualizations
if not df.empty:
    st.subheader("Visualize Your Progress")

    tab1, tab2, tab3, tab4 = st.tabs(["Sleep Trend", "Mood Trend", "Exercise Chart", "Monthly Summary"])

    with tab1:
        st.line_chart(df.set_index("Date")["Sleep"])

    with tab2:
        st.line_chart(df.set_index("Date")["Mood"])

    with tab3:
        df["Week"] = df["Date"].dt.to_period("W").astype(str)
        df["Exercise"] = df["Exercise"].map({"Yes": 1, "No": 0})
        exercise_per_week = df.groupby("Week")["Exercise"].sum()

        fig, ax = plt.subplots()
        exercise_per_week.plot(kind="bar", ax=ax, color="green")
        plt.xticks(rotation=45)
        plt.title("Exercise Days per Week")
        st.pyplot(fig)

    with tab4:
        df["Month"] = df["Date"].dt.to_period("M")
        df["Exercise"] = df["Exercise"].map({1: 1, 0: 0})
        summary = df.groupby("Month").agg({
            "Sleep": "mean",
            "Mood": "mean",
            "Exercise": "mean"
        }).round(2)
        summary["Exercise"] = summary["Exercise"] * 100

        st.dataframe(summary.rename(columns={"Exercise": "Exercise (%)"}))

else:
    st.info("No data yet. Add your first entry above!")
