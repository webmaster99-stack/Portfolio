import pytest
import tkinter as tk
from datetime import date, timedelta
import bcrypt
import psycopg2
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add application directory to path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CaloriesCalculator
from helpers.helpers import calculate_bmr, calculate_calories, calculate_daily_calories


# Mock classes and functions
class MockConnection:
    def __init__(self):
        self.cursor_mock = Mock()
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_mock

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


@pytest.fixture
def app():
    """Fixture to create the app instance with mocked Tk root"""
    root = MagicMock()
    app = CaloriesCalculator(root)
    return app


@pytest.fixture
def mock_connection():
    """Fixture to provide a mock database connection"""
    return MockConnection()


# Helper function tests
def test_calculate_bmr_male():
    """Test BMR calculation for male"""
    weight = 70
    height = 175
    sex = "male"
    age = 30

    bmr = calculate_bmr(weight, height, sex, age)
    expected = round(66 + (6.3 * weight) + (12.9 * height) - (6.8 * age))

    assert bmr == expected


def test_calculate_bmr_female():
    """Test BMR calculation for female"""
    weight = 60
    height = 165
    sex = "female"
    age = 25

    bmr = calculate_bmr(weight, height, sex, age)
    expected = round(655 + (4.3 * weight) + (4.7 * height) - (4.7 * age))

    assert bmr == expected


def test_calculate_calories():
    """Test calorie calculation based on quantity and calories per 100g"""
    quantity = 200
    calories_per_100g = 150

    calories = calculate_calories(quantity, calories_per_100g)
    expected = (quantity / 100) * calories_per_100g

    assert calories == expected


def test_calculate_daily_calories():
    """Test daily calorie calculation based on BMR and activity level"""
    bmr = 1600

    # Test each activity level
    assert calculate_daily_calories(bmr, "sedentary") == bmr * 1.2
    assert calculate_daily_calories(bmr, "lightly active") == bmr * 1.375
    assert calculate_daily_calories(bmr, "moderately active") == bmr * 1.55
    assert calculate_daily_calories(bmr, "very active") == bmr * 1.725


# Application tests
@patch('main.get_connection')
def test_login_success(mock_get_connection, app):
    """Test successful login"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock successful user query
    hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
    mock_cursor.fetchone.return_value = (1, hashed_password, 2000)  # user_id, password, daily_goal

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.username_entry = MagicMock()
    app.username_entry.get.return_value = "testuser"
    app.password_entry = MagicMock()
    app.password_entry.get.return_value = "password123"

    # Mock messagebox
    with patch('main.messagebox.showinfo') as mock_showinfo:
        with patch.object(app, 'main_menu') as mock_main_menu:
            # Call the function
            app.login_user()

            # Verify the results
            assert app.user_id == 1
            assert app.daily_goal == 2000
            mock_showinfo.assert_called_once()
            mock_main_menu.assert_called_once()


@patch('main.get_connection')
def test_login_failure(mock_get_connection, app):
    """Test failed login with incorrect password"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock failed user query (wrong password)
    hashed_password = bcrypt.hashpw("correct_password".encode('utf-8'), bcrypt.gensalt())
    mock_cursor.fetchone.return_value = (1, hashed_password, 2000)  # user_id, password, daily_goal

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.username_entry = MagicMock()
    app.username_entry.get.return_value = "testuser"
    app.password_entry = MagicMock()
    app.password_entry.get.return_value = "wrong_password"

    # Mock messagebox
    with patch('main.messagebox.showerror') as mock_showerror:
        # Call the function
        app.login_user()

        # Verify the results
        assert app.user_id is None
        mock_showerror.assert_called_once()


@patch('main.get_connection')
def test_register_user_success(mock_get_connection, app):
    """Test successful user registration"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.new_username_entry = MagicMock()
    app.new_username_entry.get.return_value = "newuser"
    app.new_password_entry = MagicMock()
    app.new_password_entry.get.return_value = "newpassword"

    # Mock messagebox and navigation
    with patch('main.messagebox.showinfo') as mock_showinfo:
        with patch.object(app, 'show_login_screen') as mock_show_login:
            # Call the function
            app.register_user()

            # Verify the results
            assert mock_conn.committed
            assert mock_conn.closed
            mock_showinfo.assert_called_once()
            mock_show_login.assert_called_once()


@patch('main.get_connection')
def test_register_user_duplicate(mock_get_connection, app):
    """Test user registration with duplicate username"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock cursor to raise integrity error on duplicate username
    mock_cursor.execute.side_effect = psycopg2.IntegrityError("duplicate key value violates unique constraint")

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.new_username_entry = MagicMock()
    app.new_username_entry.get.return_value = "existinguser"
    app.new_password_entry = MagicMock()
    app.new_password_entry.get.return_value = "password"

    # Mock messagebox
    with patch('main.messagebox.showerror') as mock_showerror:
        # Call the function
        app.register_user()

        # Verify the results
        assert mock_conn.closed
        mock_showerror.assert_called_once()


@patch('main.calculate_bmr')
@patch('main.calculate_daily_calories')
def test_calculate_daily_intake(mock_daily_calories, mock_bmr, app):
    """Test daily calorie intake calculation"""
    # Setup mocks
    mock_bmr.return_value = 1800
    mock_daily_calories.return_value = 2700

    # Set up test data
    app.weight_entry = MagicMock()
    app.weight_entry.get.return_value = "75"
    app.height_entry = MagicMock()
    app.height_entry.get.return_value = "180"
    app.age_entry = MagicMock()
    app.age_entry.get.return_value = "35"
    app.sex_entry = MagicMock()
    app.sex_entry.get.return_value = "male"
    app.activity_entry = MagicMock()
    app.activity_entry.get.return_value = "moderately active"

    # Mock messagebox
    with patch('main.messagebox.showinfo') as mock_showinfo:
        # Call the function
        app.calculate_daily_intake()

        # Verify the results
        mock_bmr.assert_called_once_with(75.0, 180.0, "male", 35)
        mock_daily_calories.assert_called_once_with(1800, "moderately active")
        mock_showinfo.assert_called_once_with("Result", "Your daily calorie intake: 2700 kcal")


@patch('main.get_connection')
def test_add_item(mock_get_connection, app):
    """Test adding a food item to the log"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1
    app.food_entry = MagicMock()
    app.food_entry.get.return_value = "Banana"
    app.quantity_entry = MagicMock()
    app.quantity_entry.get.return_value = "150"
    app.calories_entry = MagicMock()
    app.calories_entry.get.return_value = "89"
    app.meal_type_var = MagicMock()
    app.meal_type_var.get.return_value = "Snack"

    # Mock update_log_display
    with patch.object(app, 'update_log_display') as mock_update_log:
        # Call the function
        app.add_item()

        # Verify the results
        assert mock_conn.committed
        assert mock_conn.closed
        mock_cursor.execute.assert_called_once()
        mock_update_log.assert_called_once()
        # Check entry fields were cleared
        app.food_entry.delete.assert_called_with(0, tk.END)
        app.quantity_entry.delete.assert_called_with(0, tk.END)
        app.calories_entry.delete.assert_called_with(0, tk.END)


@patch('main.get_connection')
def test_update_log_display(mock_get_connection, app):
    """Test updating the log display"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock data return
    mock_cursor.fetchall.return_value = [
        (1, "Apple", 100, 52, "Snack"),
        (2, "Chicken", 200, 330, "Dinner")
    ]

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1
    app.log_listbox = MagicMock()

    # Call the function
    app.update_log_display()

    # Verify the results
    assert app.log_ids == [1, 2]
    assert mock_conn.closed
    app.log_listbox.delete.assert_called_once_with(0, tk.END)
    assert app.log_listbox.insert.call_count == 2


@patch('main.get_connection')
def test_save_goal(mock_get_connection, app):
    """Test saving a daily calorie goal"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1
    app.goal_entry = MagicMock()
    app.goal_entry.get.return_value = "2500"

    # Mock messagebox and navigation
    with patch('main.messagebox.showinfo') as mock_showinfo:
        with patch.object(app, 'main_menu') as mock_main_menu:
            # Call the function
            app.save_goal()

            # Verify the results
            assert app.daily_goal == 2500
            assert mock_conn.committed
            assert mock_conn.closed
            mock_cursor.execute.assert_called_once()
            mock_showinfo.assert_called_once()
            mock_main_menu.assert_called_once()


@patch('main.get_connection')
def test_export_logs(mock_get_connection, app, tmp_path):
    """Test exporting logs to CSV"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock data return
    mock_cursor.fetchall.return_value = [
        ("Apple", 100, 52, 52, "Snack", "2025-04-30"),
        ("Chicken", 200, 165, 330, "Dinner", "2025-04-30")
    ]

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1

    # Create temporary file path
    test_file = tmp_path / "user_1_calorie_logs.csv"

    # Mock open function to use our temp file
    mock_open = mock_open = MagicMock()

    with patch('builtins.open', mock_open):
        with patch('main.messagebox.showinfo') as mock_showinfo:
            # Call the function
            app.export_logs()

            # Verify the results
            assert mock_conn.closed
            mock_cursor.execute.assert_called_once()
            mock_open.assert_called_once()
            mock_showinfo.assert_called_once()


@patch('main.get_connection')
def test_finish_session(mock_get_connection, app):
    """Test finish session summary display"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock data return for today's calories
    mock_cursor.fetchone.return_value = [1850]

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1

    # Mock messagebox
    with patch('main.messagebox.showinfo') as mock_showinfo:
        # Call the function
        app.finish_session()

        # Verify the results
        assert mock_conn.closed
        mock_cursor.execute.assert_called_once()
        mock_showinfo.assert_called_once_with("Session Summary", "Total calories for today: 1850 kcal")


@patch('matplotlib.pyplot')
@patch('main.get_connection')
def test_show_graph(mock_get_connection, mock_plt, app):
    """Test displaying the calorie graph"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock data return
    mock_cursor.fetchall.return_value = [
        ("Apple", 150),
        ("Banana", 105),
        ("Chicken", 330)
    ]

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1

    # Call the function
    app.show_graph()

    # Verify the results
    assert mock_conn.closed
    mock_cursor.execute.assert_called_once()
    mock_plt.bar.assert_called_once()
    mock_plt.show.assert_called_once()


@patch('main.get_connection')
def test_set_daily_goal_invalid_input(mock_get_connection, app):
    """Test handling invalid input when setting daily goal"""
    # Set up test data
    app.goal_entry = MagicMock()
    app.goal_entry.get.return_value = "not_a_number"

    # Mock messagebox
    with patch('main.messagebox.showerror') as mock_showerror:
        # Call the function
        app.save_goal()

        # Verify the results
        mock_showerror.assert_called_once_with("Error", "Please enter a valid integer")


@patch('main.get_connection')
def test_remove_item(mock_get_connection, app):
    """Test removing a food item from the log"""
    # Setup mock
    mock_conn = MockConnection()
    mock_cursor = mock_conn.cursor()

    # Mock the connection function
    mock_get_connection.return_value = mock_conn

    # Set up test data
    app.user_id = 1
    app.log_listbox = MagicMock()
    app.log_listbox.curselection.return_value = [0]
    app.log_ids = [5, 6, 7]  # Mock log IDs

    # Mock update_log_display and messagebox
    with patch.object(app, 'update_log_display') as mock_update_log:
        with patch('main.messagebox.showinfo') as mock_showinfo:
            # Call the function
            app.remove_item()

            # Verify the results
            assert mock_conn.committed
            assert mock_conn.closed
            mock_cursor.execute.assert_called_once_with("DELETE FROM calorie_logs WHERE id=%s", (5,))
            mock_update_log.assert_called_once()
            mock_showinfo.assert_called_once()