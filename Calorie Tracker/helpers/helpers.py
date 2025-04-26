import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


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


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT")
    )

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(200) NOT NULL,
            daily_goal INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calorie_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            food_name VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL,
            calories_per_100g INTEGER NOT NULL,
            total_calories INTEGER NOT NULL,
            meal_type VARCHAR(50) NOT NULL,
            date DATE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_data (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()
