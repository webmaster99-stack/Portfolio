import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sqlite3
import bcrypt
import csv


# Functions for the calculations
def calculate_bmr(weight: float, height: float, sex: str, age: int) -> int:
    """Calculates the bmr of the user"""
    if sex == "male":
        bmr = 66 + (6.3 * weight) + (12.9 * height) - (6.8 * age)
    else:
        bmr = 655 + (4.3 * weight) + (4.7 * height) - (4.7 * age)
    return round(bmr)


def calculate_daily_calories(bmr: int, activity_level: str) -> int:
    """Calculates the daily calorie intake"""
    levels ={
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725
    }
    return round(bmr * levels.get(activity_level, 1.2))


def calculate_calories(food_quantity: int, calories_per_100_g: int) -> int:
    """Calculates the calories in a given food item"""
    return round((food_quantity / 100) * calories_per_100_g)


def initialize_database() -> None:
    """Creates tables for user authentication and
    calorie tracking if they don’t exist."""
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    # Create the users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            daily_goal INTEGER DEFAULT 0
        )
    """)

    # Create the calorie logs table (linked to users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calorie_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            calories_per_100g INTEGER NOT NULL,
            total_calories INTEGER NOT NULL,
            meal_type TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


class CaloriesCalculator:
    def __init__(self, root):
        self.meal_type_dropdown = None
        self.meal_type_var = None
        self.goal_entry = None
        self.log_ids = None
        self.save_edit_button = None
        self.selected_log_id = None
        self.log_listbox = None
        self.calories_entry = None
        self.quantity_entry = None
        self.food_entry = None
        self.activity_entry = None
        self.sex_entry = None
        self.age_entry = None
        self.height_entry = None
        self.weight_entry = None
        self.new_password_entry = None
        self.new_username_entry = None
        self.password_entry = None
        self.username_entry = None
        self.daily_goal = None
        self.root = root
        self.root.title("Calorie Tracker App")
        self.user_id = None
        initialize_database()  # Ensure database is initialized
        self.show_login_screen()

    def main_menu(self):
        """Displays the main menu"""
        self.clear_screen()

        menu_frame = tk.Frame(self.root, padx=20, pady=20)
        menu_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            menu_frame,
            text="Main Menu",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Button(
            menu_frame,
            text="Log Food",
            command=self.food_calories_gui
        ).grid(row=1, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Daily Calorie Calculator",
            command=self.daily_calories_gui
        ).grid(row=2, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Visualize Data",
            command=self.show_graph
        ).grid(row=3, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="View Trends",
            command=self.show_trend_graph
        ).grid(row=4, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Finish Session",
            command=self.finish_session
        ).grid(row=5, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Logout",
            command=self.show_login_screen
        ).grid(row=6, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Set Daily Calorie Goal",
            command=self.set_daily_goal
        ).grid(row=7, column=0, pady=5)

        tk.Button(
            menu_frame,
            text="Dashboard",
            command=self.show_dashboard
        ).grid(row=9, column=0, pady=5)

        if self.daily_goal is not None and self.daily_goal > 0:
            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            today_str = date.today().strftime("%Y-%m-%d")
            cursor.execute("""SELECT SUM(total_calories) 
            FROM calorie_logs 
            WHERE user_id=? 
            AND date=?""",
            (self.user_id, today_str)
            )

            result = cursor.fetchone()[0]
            conn.close()
            total_logged = int(result) if result is not None else 0
            percentage = min(int((total_logged / self.daily_goal) * 100), 100)

            progress_frame = tk.Frame(menu_frame, padx=10, pady=10)
            progress_frame.grid(row=8, column=0, pady=10)
            tk.Label(
                progress_frame,
                text=f"Today's intake: {total_logged} / {self.daily_goal} kcal"
            ).grid(row=0,column=0, pady=5)
            progress_bar = ttk.Progressbar(
                progress_frame,
                length=300,
                mode='determinate', maximum=100, value=percentage
            )
            progress_bar.grid(row=1, column=0, pady=5)
        else:
            tk.Label(
                menu_frame,
                text="No daily goal set"
            ).grid(row=8, column=0, pady=10)

    def show_login_screen(self):
        """Displays the user login screen."""
        self.clear_screen()

        login_frame = tk.Frame(self.root, padx=20, pady=20)
        login_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            login_frame,
            text="Login",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(
            login_frame,
            text="Username:"
        ).grid(row=1, column=0, sticky="e")

        self.username_entry = tk.Entry(login_frame)
        self.username_entry.grid(row=1, column=1)

        tk.Label(
            login_frame,
            text="Password:"
        ).grid(row=2, column=0, sticky="e")

        self.password_entry = tk.Entry(login_frame, show="*")
        self.password_entry.grid(row=2, column=1)

        tk.Button(
            login_frame,
            text="Login",
            command=self.login_user
        ).grid(row=3, column=0, pady=10)
        tk.Button(
            login_frame,
            text="Register",
            command=self.show_registration_screen
        ).grid(row=3, column=1, pady=10)

    def login_user(self):
        """Logs the user in """
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password, daily_goal FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
            self.user_id = user[0]
            self.daily_goal = user[2]  # Load the daily goal from the database
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.main_menu()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    def show_registration_screen(self):
        """Displays the user registration screen."""
        self.clear_screen()

        reg_frame = tk.Frame(self.root, padx=20, pady=20)
        reg_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            reg_frame,
            text="Register",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(
            reg_frame,
            text="New Username:"
        ).grid(row=1, column=0, sticky="e")

        self.new_username_entry = tk.Entry(reg_frame)
        self.new_username_entry.grid(row=1, column=1)

        tk.Label(
            reg_frame,
            text="New password:"
        ).grid(row=2, column=0, sticky="e")

        self.new_password_entry = tk.Entry(reg_frame, show="*")
        self.new_password_entry.grid(row=2, column=1)

        tk.Button(
            reg_frame,
            text="Register",
            command=self.register_user
        ).grid(row=3, column=0, pady=10)
        tk.Button(
            reg_frame,
            text="Back to Login",
            command=self.show_login_screen
        ).grid(row=3, column=1, pady=10)

    def register_user(self):
        """Creates a new user with the given username and password"""
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login_screen()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

        conn.close()


    def daily_calories_gui(self):
        """Displays the daily calories calculator screen"""
        self.clear_screen()

        calc_frame = tk.Frame(self.root, padx=20, pady=20)
        calc_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            calc_frame,
            text="Weight (kg):"
        ).grid(row=0, column=0, sticky="e")

        self.weight_entry = tk.Entry(calc_frame)
        self.weight_entry.grid(row=0, column=1)

        tk.Label(
            calc_frame,
            text="Height (cm):"
        ).grid(row=1, column=0, sticky="e")

        self.height_entry = tk.Entry(calc_frame)
        self.height_entry.grid(row=1, column=1)

        tk.Label(
            calc_frame,
            text="Age:"
        ).grid(row=2, column=0, sticky="e")

        self.age_entry = tk.Entry(calc_frame)
        self.age_entry.grid(row=2, column=1)

        tk.Label(
            calc_frame,
            text="Sex (male/female):"
        ).grid(row=3, column=0, sticky="e")

        self.sex_entry = tk.Entry(calc_frame)
        self.sex_entry.grid(row=3, column=1)

        tk.Label(
            calc_frame,
            text="Activity Level (sedentary, lightly active, moderately active, very active):"
        ).grid(row=4, column=0, sticky="e")
        self.activity_entry = tk.Entry(calc_frame)
        self.activity_entry.grid(row=4, column=1)

        tk.Button(
            calc_frame,
            text="Calculate",
            command=self.calculate_daily_intake
        ).grid(row=5, column=0, pady=10)
        tk.Button(
            calc_frame,
            text="Back",
            command=self.main_menu
        ).grid(row=5, column=1, pady=10)

    def calculate_daily_intake(self):
        """Calculates the calorie daily intake"""
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            age = int(self.age_entry.get())
            sex = self.sex_entry.get().lower()
            activity_level = self.activity_entry.get().lower()

            bmr = calculate_bmr(weight, height, sex, age)
            daily_calories = calculate_daily_calories(bmr, activity_level)

            messagebox.showinfo(
                "Result",
                f"Your daily calorie intake: {int(daily_calories)} kcal"
            )

        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")

    def food_calories_gui(self):
        """Calculates the calories in a food item"""
        self.clear_screen()

        log_frame = tk.Frame(self.root, padx=20, pady=20)
        log_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            log_frame,
            text="Food Name:"
        ).grid(row=0, column=0, sticky="e")

        self.food_entry = tk.Entry(log_frame)
        self.food_entry.grid(row=0, column=1)

        tk.Label(
            log_frame,
            text="Quantity (g):"
        ).grid(row=1, column=0, sticky="e")

        self.quantity_entry = tk.Entry(log_frame)
        self.quantity_entry.grid(row=1, column=1)

        tk.Label(
            log_frame,
            text="Calories per 100g:"
        ).grid(row=2, column=0, sticky="e")

        self.calories_entry = tk.Entry(log_frame)
        self.calories_entry.grid(row=2, column=1)

        # Meal Type Dropdown
        tk.Label(
            log_frame,
            text="Meal Type:"
        ).grid(row=3, column=0, sticky="e")

        # Options for meal type
        meal_options = ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]

        # Create a StringVar to store the selected value; default to 'Other'
        self.meal_type_var = tk.StringVar(value="Other")

        # Create the dropdown (OptionMenu) widget
        self.meal_type_dropdown = tk.OptionMenu(
            log_frame,
            self.meal_type_var,
            *meal_options
        )

        self.meal_type_dropdown.grid(row=3, column=1, sticky="w")

        # Create a frame for the action buttons
        button_frame = tk.Frame(log_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(
            button_frame,
            text="Add Item",
            command=self.add_item
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Edit Item",
            command=self.edit_item
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Remove Item",
            command=self.remove_item
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="Finish Session",
            command=self.finish_session
        ).grid(row=0, column=3, padx=5)

        tk.Button(
            button_frame,
            text="Back",
            command=self.main_menu
        ).grid(row=0, column=4, padx=5)

        # Save Edit Button (hidden by default)
        self.save_edit_button = tk.Button(
            log_frame,
            text="Save Edit",
            command=self.save_edit
        )

        self.save_edit_button.grid(row=5, column=0, columnspan=2, pady=10)
        self.save_edit_button.grid_remove()  # Hide initially

        self.log_listbox = tk.Listbox(log_frame, width=50)
        self.log_listbox.grid(row=6, column=0, columnspan=2, pady=10)
        self.update_log_display()

    def add_item(self):
        """Adds a food item to the database"""
        try:
            food_name = self.food_entry.get()
            quantity = int(self.quantity_entry.get())
            calories_per_100g = int(self.calories_entry.get())
            total_calories = calculate_calories(quantity, calories_per_100g)
            meal_type = self.meal_type_var.get()
            date_today = date.today().strftime("%Y-%m-%d")

            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calorie_logs 
                (user_id, 
                food_name, 
                quantity, 
                calories_per_100g, 
                total_calories, 
                meal_type, 
                date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.user_id,
                food_name,
                quantity,
                calories_per_100g,
                total_calories,
                meal_type, date_today
            )
            )
            conn.commit()
            conn.close()

            self.update_log_display()
            self.food_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.calories_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")

    def update_log_display(self):
        self.log_listbox.delete(0, tk.END)
        self.log_ids = []  # Store the corresponding log IDs
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id,
             food_name, 
             quantity, 
             total_calories, 
             meal_type 
             FROM calorie_logs WHERE user_id=?""",
            (self.user_id,))
        logs = cursor.fetchall()
        conn.close()

        for log in logs:
            self.log_ids.append(log[0])
            # Format: Food Name - Quantity(g) - Calories kcal - Meal Type
            self.log_listbox.insert(tk.END, f"{log[1]} - {log[2]}g - {int(log[3])} kcal - {log[4]}")

    def edit_item(self):
        try:
            index = self.log_listbox.curselection()[0]
            self.selected_log_id = self.log_ids[index]  # Use the stored ID

            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            cursor.execute("""SELECT food_name, 
            quantity, 
            calories_per_100g 
            FROM calorie_logs 
            WHERE id=?""",
            (self.selected_log_id,)
            )

            log = cursor.fetchone()
            conn.close()

            self.food_entry.delete(0, tk.END)
            self.food_entry.insert(0, log[0])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, log[1])
            self.calories_entry.delete(0, tk.END)
            self.calories_entry.insert(0, log[2])

            # Show the save edit button
            self.save_edit_button.grid()

        except IndexError:
            messagebox.showerror("Error", "Please select an item to edit.")


    def save_edit(self):
        """Saves the made edits to the chosen item from the listbox"""
        try:
            food_name = self.food_entry.get()
            quantity = int(self.quantity_entry.get())
            calories_per_100g = int(self.calories_entry.get())
            total_calories = (quantity / 100) * calories_per_100g
            meal_type = self.meal_type_var.get()  # Include meal type

            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE calorie_logs
                    SET food_name=?, 
                    quantity=?, 
                    calories_per_100g=?, 
                    total_calories=?, 
                    meal_type=?
                    WHERE id=?
                """, (
                food_name,
                quantity,
                calories_per_100g,
                total_calories,
                meal_type,
                self.selected_log_id
            )
                           )

            conn.commit()
            conn.close()

            self.update_log_display()
            messagebox.showinfo("Success", "Item updated successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")

    def remove_item(self):
        try:
            index = self.log_listbox.curselection()[0]
            log_id = self.log_ids[index]  # Get the ID from the stored list

            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calorie_logs WHERE id=?", (log_id,))
            conn.commit()
            conn.close()

            self.update_log_display()
            messagebox.showinfo("Success", "Item removed successfully!")

        except IndexError:
            messagebox.showerror("Error", "Please select an item to remove.")

    def finish_session(self):
        """Finishes the current session and displays a summary"""
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT SUM(total_calories) 
            FROM calorie_logs 
            WHERE user_id=? AND date=?""",
            (self.user_id, date.today().strftime("%Y-%m-%d"))
        )

        total_calories = cursor.fetchone()[0]
        conn.close()

        if total_calories:
            messagebox.showinfo(
                "Session Summary",
                f"Total calories for today: {int(total_calories)} kcal"
            )
        else:
            messagebox.showinfo(
                "Session Summary",
                "No items logged today."
            )

    def show_graph(self):
        """Displays a bar graph with the data from the database"""
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT food_name, 
            SUM(total_calories) 
            FROM calorie_logs 
            WHERE user_id=? 
            GROUP BY food_name""",
            (self.user_id,)
        )
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Info", "No data to display.")
            return

        food_names, calories = zip(*data)
        plt.bar(food_names, calories, color='skyblue')
        plt.xlabel("Food Items")
        plt.ylabel("Calories")
        plt.title("Calorie Intake")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_trend_graph(self):
        """Displays a trend graph"""
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT date, 
            SUM(total_calories) 
            FROM calorie_logs 
            WHERE user_id=? 
            GROUP BY date""",
            (self.user_id,)
        )

        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Info", "No data to display.")
            return

        dates, total_calories = zip(*data)
        plt.plot(dates, total_calories, marker='o')
        plt.xlabel("Date")
        plt.ylabel("Total Calories")
        plt.title("Calorie Intake Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def set_daily_goal(self):
        self.clear_screen()

        goal_frame = tk.Frame(self.root, padx=20, pady=20)
        goal_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(goal_frame,
                 text="Set Daily Goal",
                 font=("Arial", 18, "bold")
                 ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(
            goal_frame,
            text="Goal (kcal):"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.goal_entry = tk.Entry(goal_frame)
        self.goal_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(
            goal_frame,
            text="Save Goal",
            command=self.save_goal
        ).grid(row=2, column=0, pady=10)

        tk.Button(
            goal_frame,
            text="Back",
            command=self.main_menu
        ).grid(row=2, column=1, pady=10)

    def save_goal(self):
        try:
            new_goal = int(self.goal_entry.get())
            self.daily_goal = new_goal

            # Update the user's daily goal in the database
            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET daily_goal=? WHERE id=?",
                (new_goal, self.user_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Daily goal set to {self.daily_goal} kcal"
            )

            self.main_menu()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer")


    def export_logs(self):
        """Exports the logs of the current user to a csv file"""
        # Query the database for the current user's logs
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()

        cursor.execute(
            """SELECT food_name, 
            quantity, 
            calories_per_100g, 
            total_calories, 
            meal_type, 
            date 
            FROM calorie_logs 
            WHERE user_id=?""",
            (self.user_id,)
        )

        logs = cursor.fetchall()
        conn.close()

        if not logs:
            messagebox.showinfo("Export Logs", "No logs available to export")
            return

        filename = f"user_{self.user_id}_calorie_logs.csv"

        try:
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write header row
                writer.writerow(
                    [
                    "Food Name",
                    "Quantity (g)",
                    "Calories per 100g",
                    "Total Calories",
                    "Meal Type",
                    "Date"
                ]
                )
                # Write each log entry
                for log in logs:
                    writer.writerow(log)

            messagebox.showinfo("Export Logs", f"Logs exported successfully to {filename}")

        except Exception as e:
            messagebox.showerror("Export Logs", f"An error occurred: {str(e)}")

    def show_dashboard(self):
        self.clear_screen()

        # Create the dashboard frame
        dashboard_frame = tk.Frame(self.root, padx=20, pady=20)
        dashboard_frame.grid(row=0, column=0, padx=50, pady=50)

        tk.Label(
            dashboard_frame,
            text="User Dashboard",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2,pady=10)

        # Query the last 7 days od data
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()

        days = []
        totals = []

        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            days.append(day_str)

            cursor.execute("""SELECT SUM(total_calories) 
            FROM calorie_logs 
            WHERE user_id=? AND date=?""", (self.user_id, day_str))
            result = cursor.fetchone()[0]
            totals.append(result if result is not None else 0)

        conn.close()

        # Create a line chart using matplotlib
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(days, totals, marker="o")
        ax.set_title("Daily Calorie Intake (Last 7 Days)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Calories")
        ax.tick_params(axis="x", rotation=45, labelsize=10)
        fig.autofmt_xdate()
        fig.subplots_adjust(bottom=0.3)

        canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, pady=10)

        # Calculate and display the average daily intake
        avg_intake = sum(totals) / 7

        tk.Label(
            dashboard_frame,
            text=f"Average Daily Intake: {int(avg_intake)} kcal",
            font=("Arial", 14)
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # Button to return to the main menu
        tk.Button(
            dashboard_frame,
            text="Back",
            command=self.main_menu
        ).grid(row=3, column=0, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = CaloriesCalculator(root)
    root.mainloop()