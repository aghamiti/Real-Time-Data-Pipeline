import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QMessageBox, QWidget, QHBoxLayout, QGridLayout, QFrame, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import plotly.express as px
import subprocess
import sys


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Data Viewer")
        self.setGeometry(100, 100, 900, 600)

        # Apply background gradient
        self.setStyleSheet("""
            background: linear-gradient(to bottom, #ffffff, #e0f7fa);
        """)

        # Main Layout
        self.central_widget = QStackedWidget()  # Stacked widget for multiple pages
        self.setCentralWidget(self.central_widget)

        # Main Page
        self.main_page = QWidget()
        self.main_layout = QVBoxLayout(self.main_page)

        # Header Section with Image and Description
        self.header_layout = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout)

        # Header Image
        self.header_image = QLabel()
        header_pixmap = QPixmap("icons/yes.png").scaled(80, 80, Qt.KeepAspectRatio)
        self.header_image.setPixmap(header_pixmap)
        self.header_layout.addWidget(self.header_image)

        # Header Description Text
        self.header_description = QLabel("Welcome to the Weather Data Viewer. Select a city to view weather details.")
        self.header_description.setFont(QFont("Arial", 12))
        self.header_layout.addWidget(self.header_description)

        # Dropdown and Button Section (Side-by-Side Layout)
        self.input_layout = QVBoxLayout()  # Changed to vertical layout
        self.main_layout.addLayout(self.input_layout)

        # Dropdown for City Selection
        self.city_label = QLabel("Select City:")
        self.city_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_layout.addWidget(self.city_label)

        self.city_dropdown = QComboBox()
        self.city_dropdown.addItems(cities)
        self.city_dropdown.setStyleSheet("padding: 5px; font-size: 14px;")
        self.input_layout.addWidget(self.city_dropdown)

        # Description above Submit Button
        self.submit_description = QLabel("Click to view weather details for the selected city.")
        self.submit_description.setFont(QFont("Arial", 10))
        self.input_layout.addWidget(self.submit_description)

        # Submit Button
        self.submit_button = QPushButton("Show Weather")
        self.submit_button.setStyleSheet("""
            background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px;
            padding: 10px 20px;
        """)
        self.submit_button.clicked.connect(self.on_submit)
        self.input_layout.addWidget(self.submit_button)

        # Add vertical spacing between buttons
        self.input_layout.addSpacing(20)

        # Description above Compare Cities Text Box
        self.compare_description = QLabel("Enter comma-separated cities to compare their weather.")
        self.compare_description.setFont(QFont("Arial", 10))
        self.input_layout.addWidget(self.compare_description)

        # Text Box for Compare Cities
        self.city_input = QLineEdit()
        self.city_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.input_layout.addWidget(self.city_input)

        # Compare Cities Button
        self.compare_button = QPushButton("Compare Cities")
        self.compare_button.setStyleSheet("""
            background-color: #f76c5e; color: white; font-weight: bold; font-size: 14px;
            padding: 10px 20px;
        """)
        self.compare_button.clicked.connect(self.compare_cities)
        self.input_layout.addWidget(self.compare_button)

        # Add vertical spacing between buttons
        self.input_layout.addSpacing(20)

        # Description above Refresh Button
        self.refresh_description = QLabel("Click to refresh the weather data from the database.")
        self.refresh_description.setFont(QFont("Arial", 10))
        self.input_layout.addWidget(self.refresh_description)

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("""
            background-color: #2196F3; color: white; font-weight: bold; font-size: 14px;
            padding: 10px 20px;
        """)
        self.refresh_button.clicked.connect(self.run_second_script)
        self.input_layout.addWidget(self.refresh_button)

        # Add Main Page to Central Widget
        self.central_widget.addWidget(self.main_page)

        # Weather Details Page
        self.weather_page = QWidget()
        self.weather_layout = QVBoxLayout(self.weather_page)

        # Back Button
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet(
            "background-color: #f44336; color: white; font-weight: bold; font-size: 14px; padding: 5px 15px;"
        )
        self.back_button.clicked.connect(self.go_back)
        self.weather_layout.addWidget(self.back_button)

        # Weather Card Display (Layout updated to allow space for an image)
        self.weather_card = QFrame()
        self.weather_card.setStyleSheet(
            "background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);"
        )
        self.weather_card_layout = QGridLayout(self.weather_card)
        self.weather_layout.addWidget(self.weather_card)

        # Add Weather Page to Central Widget
        self.central_widget.addWidget(self.weather_page)

    def fetch_weather_data(self, city_name):
        conn = sqlite3.connect('weather_data.db')
        query = (
            "SELECT time, name, temp, feels_like, temp_min, temp_max, humidity, wind_speed, sunrise, sunset, "
            "country, weather_type FROM weather_data WHERE name = ?"
        )
        df = pd.read_sql_query(query, conn, params=(city_name,))
        conn.close()

        if df.empty:
            QMessageBox.critical(self, "Error", f"No data found for city: {city_name}")
            return None, None

        df['time'] = pd.to_datetime(df['time'])
        latest_time = df['time'].max()
        return df, latest_time

    def on_submit(self):
        city_name = self.city_dropdown.currentText()
        df, latest_time = self.fetch_weather_data(city_name)

        if df is not None:
            self.display_weather_data(df, latest_time)

    def display_weather_data(self, df, latest_time):
        # Clear previous widgets
        for i in reversed(range(self.weather_card_layout.count())):
            self.weather_card_layout.itemAt(i).widget().setParent(None)

        # Dynamic Icons Based on Weather Description and Humidity
        humidity = df['humidity'].iloc[-1]
        weather_type = df['weather_type'].iloc[-1].lower()

        if humidity > 80:
            icon_path = "icons/high_humidity.png"
        elif "rain" in weather_type:
            icon_path = "icons/rain.png"
        elif "clear" in weather_type:
            icon_path = "icons/sunny.png"
        else:
            icon_path = "icons/cloudy.png"

        # Weather Card Layout Adjustments
        self.weather_card_layout.setColumnStretch(0, 1)
        self.weather_card_layout.setColumnStretch(1, 3)

        # Add weather icon at the top-left
        weather_icon = QLabel()
        weather_icon.setPixmap(QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio))
        self.weather_card_layout.addWidget(weather_icon, 0, 0, 1, 2, Qt.AlignCenter)

        # Display Weather Data
        city_name = df['name'].iloc[-1]
        country = df['country'].iloc[-1]
        fields = [
            "Temperature", "Feels Like", "Min Temperature", "Max Temperature",
            "Humidity", "Wind Speed", "Sunrise", "Sunset", "Weather Type"
        ]
        values = [
            f"{df['temp'].iloc[-1]:.1f}°C",
            f"{df['feels_like'].iloc[-1]:.1f}°C",
            f"{df['temp_min'].iloc[-1]:.1f}°C",
            f"{df['temp_max'].iloc[-1]:.1f}°C",
            f"{df['humidity'].iloc[-1]}%",
            f"{df['wind_speed'].iloc[-1]} m/s",
            df['sunrise'].iloc[-1],
            df['sunset'].iloc[-1],
            df['weather_type'].iloc[-1]
        ]

        # Add city and country as the title
        weather_description = QLabel(f"{city_name}, {country}")
        weather_description.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.weather_card_layout.addWidget(weather_description, 1, 0, 1, 2, Qt.AlignCenter)

        # Add fields and values in two columns
        for i, (field, value) in enumerate(zip(fields, values)):
            label = QLabel(f"{field}:")
            label.setStyleSheet("font-weight: bold; font-size: 12px;")
            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 12px;")

            # Left and right alignment
            if i % 2 == 0:  # Left column
                self.weather_card_layout.addWidget(label, (i // 2) + 2, 0)
                self.weather_card_layout.addWidget(value_label, (i // 2) + 2, 1)
            else:  # Right column
                self.weather_card_layout.addWidget(label, (i // 2) + 2, 2)
                self.weather_card_layout.addWidget(value_label, (i // 2) + 2, 3)

        # Switch to Weather Page
        self.central_widget.setCurrentWidget(self.weather_page)

    def compare_cities(self):
        cities = self.city_input.text().split(", ")
        combined_df = pd.DataFrame()

        for city in cities:
            df, _ = self.fetch_weather_data(city)
            if df is not None:
                combined_df = pd.concat([combined_df, df], ignore_index=True)

        if combined_df.empty:
            QMessageBox.critical(self, "Error", "No data available for the selected cities")
            return

        fig = px.line(
            combined_df, x='time', y='temp', color='name',
            title="Temperature Comparison for Selected Cities",
            labels={"time": "Time", "temp": "Temperature (°C)", "name": "City"},
            template="plotly_dark"
        )
        fig.show()

    def run_second_script(self):
        try:
            subprocess.run(['python', 'second.py'], check=True)
            QMessageBox.information(self, "Success", "second.py script executed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run second.py script: {e}")

    def go_back(self):
        self.central_widget.setCurrentWidget(self.main_page)


# City List
cities = [
    "Moscow", "Istanbul", "London", "Berlin", "Madrid", "Rome", "Paris", "Kiev", "Hamburg", "Warsaw", "Vienna",
    "Athens", "Milan", "Munich", "Stockholm", "Dublin", "Oslo", "Copenhagen", "Brussels"
]

# Run Application
app = QApplication(sys.argv)
window = WeatherApp()
window.show()
sys.exit(app.exec_())
