# Calorie Tracker App Documentation

## Overview

The Calorie Tracker App is a comprehensive Python application built using Tkinter and SQLite. It allows users to:

- **Register and Log In:** Secure user authentication with password hashing.
- **Log Food Entries:** Record food items with details such as quantity, calories per 100g, and meal type (e.g., Breakfast, Lunch, Dinner, Snack, Other).
- **Calculate Daily Calorie Needs:** Based on personal data (weight, height, age, sex) and activity level.
- **Set Daily Calorie Goals & Track Progress:** Users can set a daily calorie target and view progress with a progress bar.
- **View Advanced Analytics Dashboard:** Visualize calorie trends over the past 7 days with embedded Matplotlib charts.
- **Export Food Logs:** Export your food logs to a CSV file for offline analysis.

## Table of Contents

- [Features](#features)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
  - [User Authentication](#user-authentication)
  - [Food Logging](#food-logging)
  - [Daily Calorie Calculator](#daily-calorie-calculator)
  - [Daily Goal & Progress Tracking](#daily-goal-and-progress-tracking)
  - [Dashboard & Analytics](#dashboard--analytics)
  - [Export Logs](#export-logs)
- [Author](#author)

## Features

-**User Authentication:**  
  - Registration and login with password hashing (using `bcrypt`).
  - User data is stored in an SQLite database.
  
- **Food Logging with Meal Categorization:**  
  - Users can log food entries with details including food name, quantity, calories per 100g, and meal type.
  - Food entries are stored with a timestamp (date in ISO format).

- **Daily Calorie Calculator:**  
  - Users can calculate their daily calorie needs based on BMR and an activity multiplier.
  
- **Daily Goal & Progress Tracking:**  
  - Users can set a daily calorie goal that is stored persistently in the database.
  - The app displays a progress bar showing the total calories logged for the current day relative to the goal.

- **Dashboard & Advanced Analytics:**  
  - A dedicated dashboard screen shows a 7-day trend of calorie intake via an embedded Matplotlib line chart.
  - It displays summary statistics, such as the average daily calorie intake.

- **Export Functionality:**  
  - Users can export their food logs to a CSV file.


## Database Schema

The app uses an SQLite database (`calories.db`) with two primary tables:

1. **`users` Table:**
   - `id`: Primary key.
   - `username`: Unique username.
   - `password`: Hashed password.
   - `daily_goal`: User’s daily calorie goal (integer, default 0).

2. **`calorie_logs` Table:**
   - `id`: Primary key.
   - `user_id`: Foreign key referencing `users.id`.
   - `food_name`: Name of the food item.
   - `quantity`: Quantity in grams.
   - `calories_per_100g`: Calories per 100 grams.
   - `total_calories`: Calculated total calories for the entry.
   - `meal_type`: Meal category (Breakfast, Lunch, Dinner, Snack, Other).
   - `date`: Date of the log entry (ISO format, e.g., `YYYY-MM-DD`).

## Installation

1. **Dependencies:**
   - Python 3.x
   - Tkinter (included with Python)
   - `sqlite3` (included with Python)
   - `bcrypt` (install with `pip install bcrypt`)
   - `matplotlib` (install with `pip install matplotlib`)

2. **Clone or Download the Repository:**  
   Ensure all the source files (including the main Python script and this documentation) are in the same directory.

3. **Run the Application:**
   ```bash
   python main.py
   
## Usage
## User Authentication
### Registration:
 - New users can register by providing a unique username and a password. Passwords are hashed using bcrypt before storing in the database.

### Login:
 - Returning users log in with their credentials. Upon login, the app loads the user's daily goal (if set) and food logs.

## Food Logging
### Logging Food:
 - In the "Log Food" section, users can enter:

 - Food Name
 - Quantity (in grams)
 - Calories per 100g
 - Meal Type (selected from a dropdown: Breakfast, Lunch, Dinner, Snack, Other)
 - Editing & Removing:
Users can select an entry from the list, edit it (using the "Edit Item" button, then "Save Edit"), or remove it using the "Remove Item" button.

### Finishing a Session:
 - The `Finish Session` button displays the total calories logged for the current day.

## Daily Calorie Calculator
 - Users can calculate their daily calorie needs by entering:
 - Weight (kg)
 - Height (cm)
 - Age
 - Sex (male/female)
 - Activity Level (sedentary, lightly active, moderately active, very active)
 - The app calculates and displays the estimated daily calorie requirement.

## Daily Goal and Progress Tracking
### Setting a Goal:
 - Users can set a daily calorie goal, which is stored in the database.

### Progress Display:
 - In the main menu, a progress section shows:

 - Total calories logged for the current day.
 - A progress bar indicating the percentage of the daily goal achieved.

## Dashboard & Analytics
### Dashboard Screen:
 - The dashboard shows a 7-day trend of calorie intake with a line chart and displays the average daily intake.

### Visualization:
- Uses Matplotlib to embed charts in the app, with proper formatting and label rotation for readability.

## Export Logs
### Export Functionality:
 - Users can export their food logs to a CSV file, which is saved with a filename that includes the user's ID.

## Author
- This project was created by Ilian Hadzhidimitrov 
