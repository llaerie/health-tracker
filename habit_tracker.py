import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime

# Create main window
root = tk.Tk()
root.title("Health Habit Tracker")

# Labels and entry fields
tk.Label(root, text="Hours of Sleep:").grid(row=0, column=0)
sleep_entry = tk.Entry(root)
sleep_entry.grid(row=0, column=1)

tk.Label(root, text="Mood (1-10):").grid(row=1, column=0)
mood_entry = tk.Entry(root)
mood_entry.grid(row=1, column=1)

exercise_var = tk.IntVar()
exercise_check = tk.Checkbutton(root, text="Exercised Today?", variable=exercise_var)
exercise_check.grid(row=2, columnspan=2)

tk.Label(root, text="Notes:").grid(row=3, column=0)
notes_entry = tk.Entry(root, width=30)
notes_entry.grid(row=3, column=1)

# Function to save input to CSV
def save_data():
    date = datetime.now().strftime("%Y-%m-%d")
    sleep = sleep_entry.get()
    mood = mood_entry.get()
    exercised = "Yes" if exercise_var.get() else "No"
    notes = notes_entry.get()

    if not sleep or not mood:
        messagebox.showwarning("Missing Info", "Please fill out all required fields.")
        return

    with open("habit_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, sleep, mood, exercised, notes])

    messagebox.showinfo("Success", "Entry saved!")
    sleep_entry.delete(0, tk.END)
    mood_entry.delete(0, tk.END)
    exercise_var.set(0)
    notes_entry.delete(0, tk.END)

import pandas as pd
import matplotlib.pyplot as plt

def plot_sleep():
    try:
        df = pd.read_csv("habit_data.csv", header=None,
                         names=["Date", "Sleep", "Mood", "Exercise", "Notes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Sleep"] = pd.to_numeric(df["Sleep"], errors="coerce")
        df = df.dropna()

        plt.figure(figsize=(8, 4))
        plt.plot(df["Date"], df["Sleep"], marker='o', color='purple')
        plt.title("Sleep Over Time")
        plt.xlabel("Date")
        plt.ylabel("Hours of Sleep")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def plot_mood():
    try:
        df = pd.read_csv("habit_data.csv", header=None,
                         names=["Date", "Sleep", "Mood", "Exercise", "Notes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Mood"] = pd.to_numeric(df["Mood"], errors="coerce")
        df = df.dropna()

        plt.figure(figsize=(8, 4))
        plt.plot(df["Date"], df["Mood"], marker='o', color='blue')
        plt.title("Mood Over Time")
        plt.xlabel("Date")
        plt.ylabel("Mood (1–10)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def plot_exercise():
    try:
        df = pd.read_csv("habit_data.csv", header=None,
                         names=["Date", "Sleep", "Mood", "Exercise", "Notes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Week"] = df["Date"].dt.to_period("W").astype(str)
        df["Exercise"] = df["Exercise"].map({"Yes": 1, "No": 0})

        exercise_per_week = df.groupby("Week")["Exercise"].sum()

        plt.figure(figsize=(8, 4))
        exercise_per_week.plot(kind="bar", color="green")
        plt.title("Exercise Days per Week")
        plt.xlabel("Week")
        plt.ylabel("Days Exercised")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_summary():
    try:
        df = pd.read_csv("habit_data.csv", header=None,
                         names=["Date", "Sleep", "Mood", "Exercise", "Notes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")
        df["Sleep"] = pd.to_numeric(df["Sleep"], errors="coerce")
        df["Mood"] = pd.to_numeric(df["Mood"], errors="coerce")
        df["Exercise"] = df["Exercise"].map({"Yes": 1, "No": 0})

        summary = df.groupby("Month").agg({
            "Sleep": "mean",
            "Mood": "mean",
            "Exercise": "mean"
        }).round(2)

        summary["Exercise"] = summary["Exercise"] * 100  # convert to %

        message = ""
        for idx, row in summary.iterrows():
            message += f"{idx}:\n"
            message += f" - Avg Sleep: {row['Sleep']} hrs\n"
            message += f" - Avg Mood: {row['Mood']}/10\n"
            message += f" - Days Exercised: {row['Exercise']}%\n\n"

        messagebox.showinfo("Monthly Summary", message)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Submit button
submit_btn = tk.Button(root, text="Save Entry", command=save_data)
submit_btn.grid(row=4, columnspan=2, pady=10)

# Plot data buttons
plot_sleep_btn = tk.Button(root, text="Plot Sleep", command=plot_sleep)
plot_sleep_btn.grid(row=5, column=0)

plot_mood_btn = tk.Button(root, text="Plot Mood", command=plot_mood)
plot_mood_btn.grid(row=5, column=1)

plot_exercise_btn = tk.Button(root, text="Plot Exercise", command=plot_exercise)
plot_exercise_btn.grid(row=6, columnspan=2, pady=5)

# Summary button
summary_btn = tk.Button(root, text="Show Monthly Summary", command=show_summary)
summary_btn.grid(row=7, columnspan=2, pady=10)

root.mainloop()
