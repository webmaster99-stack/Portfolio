# Coffee And Wi-Fi

## Project Overview

Coffee And Wi-Fi is a Flask-based web application that allows users to view and add cafés with information about power socket availability, Wi-Fi strength, and coffee quality. The application uses Flask-WTF for form handling and Flask-Bootstrap for styling.

## Features

- View a list of cafés with details on power socket availability, Wi-Fi strength, and coffee quality.
- Add new cafés to the database.
- Navigate between the home page, add cafe page, and view cafés page.

## Technologies Used

- Python
- Flask
- Flask-Bootstrap
- Flask-WTF
- WTForms
- HTML
- CSV

## Project Structure

CoffeeAndWifi/
│
├── templates/
│   ├── add.html
│   ├── base.html
│   ├── cafes.html
│   └── index.html
│
├── main.py
├── cafe-data.csv
├── requirements.txt
└── README.md

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/CoffeeAndWifi.git
    cd CoffeeAndWifi
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Ensure the virtual environment is activated.
2. Run the Flask application:
    ```sh
    python main.py
    ```
3. Open your web browser and navigate to `http://127.0.0.1:5000/`.

## File Descriptions

### `main.py`

This is the main application file that contains the Flask routes and form handling logic.

### `templates/`

This directory contains the HTML templates for the application.

- `base.html`: The base template that other templates extend.
- `index.html`: The home page template.
- `add.html`: The template for adding a new cafe.
- `cafes.html`: The template for displaying the list of cafés.

### `cafe-data.csv`

This file stores the cafe data in CSV format.

### `requirements.txt`

This file lists the Python dependencies required for the project.

## Routes

- `/`: Home page displaying the introduction and a button to view cafés.
- `/add`: Page to add a new cafe to the database.
- `/cafes`: Page to view the list of all cafés.

## Forms

### `CafeForm`

A Flask-WTF form for adding a new cafe with the following fields:
- `cafe`: Cafe name (StringField)
- `location`: Cafe location on Google Maps (URL) (StringField)
- `open`: Opening time (StringField)
- `close`: Closing time (StringField)
- `coffee_rating`: Coffee rating (SelectField)
- `wifi_rating`: Wi-Fi strength rating (SelectField)
- `power_rating`: Power socket availability (SelectField)
- `submit`: Submit button (SubmitField)

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.