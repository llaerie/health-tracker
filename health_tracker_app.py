# ----- LOGIN SETUP -----
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

USERS = st.secrets["users"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""


def login_or_signup():
    st.title("Health Habit Tracker Login")

    option = st.radio("Choose Option", ["Login", "Sign Up"])

    if option == "Login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                try:
                    users_df = pd.read_csv("users.csv")
                    user_row = users_df[users_df["username"] == username]
                    if not user_row.empty and user_row.iloc[0]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        # Remove experimental_rerun() and let the user see the app after login
                    else:
                        st.error("Invalid username or password.")
                except FileNotFoundError:
                    st.error("No users registered yet.")

    elif option == "Sign Up":
        with st.form("signup_form"):
            new_user = st.text_input("Choose a username")
            new_pass = st.text_input("Choose a password", type="password")
            submit = st.form_submit_button("Create Account")
            if submit:
                if new_user == "" or new_pass == "":
                    st.warning("Username and password cannot be empty.")
                else:
                    try:
                        users_df = pd.read_csv("users.csv")
                    except FileNotFoundError:
                        users_df = pd.DataFrame(columns=["username", "password"])

                    if new_user in users_df["username"].values:
                        st.warning("Username already exists.")
                    else:
                        new_row = pd.DataFrame({"username": [new_user], "password": [new_pass]})
                        users_df = pd.concat([users_df, new_row], ignore_index=True)
                        users_df.to_csv("users.csv", index=False)
                        st.success("Account created. Please log in.")

if not st.session_state.authenticated:
    login_or_signup()
    st.stop()  # stops the rest of the app from running unless logged in

if st.session_state.authenticated:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.experimental_rerun()

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
filename = f"data_{st.session_state.username}.csv"
if submitted:
    new_entry = pd.DataFrame({
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Sleep": [sleep],
        "Mood": [mood],
        "Exercise": ["Yes" if exercise else "No"],
        "Notes": [notes]
    })

    try:
        df = pd.read_csv(filename)
        df = pd.concat([df, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry

    df.to_csv(filename, index=False)
    st.success("Entry saved!")

# Load data
try:
    df = pd.read_csv(filename)
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

# Edit/Delete Past Entries
st.subheader("Your Past Entries")

if not df.empty:
    df = df.sort_values(by="Date", ascending=False)
    df_display = df.reset_index(drop=True)

    selected_index = st.selectbox("Select an entry to edit or delete", df_display.index)
    selected_entry = df_display.loc[selected_index]

    st.write("Selected Entry:")
    st.write(selected_entry)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Entry"):
            df_display = df_display.drop(selected_index)
            df_display.to_csv(filename, index=False)
            st.success("Entry deleted.")
            st.experimental_rerun()

    with col2:
        st.write("Edit Entry")
        new_sleep = st.slider("Sleep (hrs)", 0, 12, int(selected_entry["Sleep"]))
        new_mood = st.slider("Mood (1-10)", 1, 10, int(selected_entry["Mood"]))
        new_exercise = st.checkbox("Exercised?", selected_entry["Exercise"] == "Yes")
        new_notes = st.text_input("Notes", selected_entry["Notes"])

        if st.button("Save Changes"):
            df_display.at[selected_index, "Sleep"] = new_sleep
            df_display.at[selected_index, "Mood"] = new_mood
            df_display.at[selected_index, "Exercise"] = "Yes" if new_exercise else "No"
            df_display.at[selected_index, "Notes"] = new_notes
            df_display.to_csv(filename, index=False)
            st.success("Entry updated.")
            st.experimental_rerun()

# Anonymous Data Trends
st.subheader("Anonymous Trends Across All Users")

import glob
import os

all_files = glob.glob("data_*.csv")
all_data = []

for file in all_files:
    try:
        df = pd.read_csv(file)
        df["Date"] = pd.to_datetime(df["Date"])
        all_data.append(df)
    except:
        continue

if all_data:
    df_all = pd.concat(all_data)
    st.write("Average Sleep and Mood (All Users)")

    df_all["Date"] = pd.to_datetime(df_all["Date"])
    df_all["Week"] = df_all["Date"].dt.to_period("W").astype(str)

    weekly_avg = df_all.groupby("Week")[["Sleep", "Mood"]].mean()

    st.line_chart(weekly_avg)
else:
    st.info("No user data found yet.")

# Correlation between mood, sleep, exercise
import seaborn as sns
import numpy as np

st.subheader("Mood vs Sleep and Exercise")

if len(df) >= 5:  # Require at least a few entries
    df_corr = df.copy()
    df_corr["Exercise"] = df_corr["Exercise"].map({"Yes": 1, "No": 0})
    df_corr = df_corr[["Sleep", "Mood", "Exercise"]]

    st.write("Correlation Heatmap")
    corr = df_corr.corr()
    fig = sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    st.pyplot(fig.figure)

    st.write("Scatterplot: Sleep vs Mood")
    st.scatter_chart(df[["Sleep", "Mood"]])
else:
    st.info("Add at least 5 entries to see meaningful correlation visuals.")

# Personalized Tips
st.subheader("Your Personalized Health Insights")

tips = []

if len(df) >= 5:
    avg_sleep = df["Sleep"].mean()
    avg_mood = df["Mood"].mean()
    avg_mood_when_exercise = df[df["Exercise"] == "Yes"]["Mood"].mean()
    avg_mood_no_exercise = df[df["Exercise"] == "No"]["Mood"].mean()

    # Sleep tip
    if avg_sleep >= 8:
        tips.append("You tend to sleep 8+ hours on average. Great job maintaining good sleep habits!")
    else:
        tips.append("Try getting 8+ hours of sleep. Your average is below that, which may affect your mood and energy.")

    # Exercise tip
    if avg_mood_when_exercise > avg_mood_no_exercise:
        tips.append(
            f"Your mood tends to be higher when you exercise ({avg_mood_when_exercise:.1f} vs {avg_mood_no_exercise:.1f}). Keep it up!")
    elif avg_mood_when_exercise < avg_mood_no_exercise:
        tips.append(
            "Interestingly, your mood seems slightly lower when you exercise. Consider the intensity or type of activity.")

    # Mood range
    if avg_mood >= 7:
        tips.append("Your average mood is great! Keep doing what works.")
    else:
        tips.append("Your average mood is a bit low—consider tracking what days feel best to find helpful patterns.")

    for t in tips:
        st.success(t)
else:
    st.info("Add more entries to generate personalized insights.")

# Calendar View for Entries
import plotly.express as px

st.subheader("Calendar Heatmap of Entries")

df_calendar = df.copy()
df_calendar["Date"] = pd.to_datetime(df_calendar["Date"])
df_calendar["Count"] = 1  # One log per day

daily_logs = df_calendar.groupby(df_calendar["Date"].dt.date)["Count"].count().reset_index()
daily_logs.columns = ["Date", "Logs"]

fig = px.density_heatmap(
    daily_logs,
    x="Date",
    y=["Logs"]*len(daily_logs),  # trick to create a single-row calendar style
    nbinsx=31,
    color_continuous_scale="Blues",
    title="Daily Logging Activity",
)
fig.update_layout(yaxis=dict(showticklabels=False))

st.plotly_chart(fig)