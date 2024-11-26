import sqlite3
import pandas as pd
import plotly.express as px
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QWidget,
    QMessageBox,
    QLineEdit,
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import subprocess
import webbrowser


# Function to fetch weather data
def fetch_weather_data(city_name):
    conn = sqlite3.connect("weather_data.db")
    query = f"SELECT time, name, temp, feels_like, temp_min, temp_max, humidity, wind_speed FROM weather_data WHERE name = ?"
    df = pd.read_sql_query(query, conn, params=(city_name,))
    conn.close()

    if df.empty:
        return None, None

    df["time"] = pd.to_datetime(df["time"])
    latest_time = df["time"].max()
    return df, latest_time


# Function to fetch and combine data for multiple cities
def fetch_weather_for_cities(cities):
    combined_df = pd.DataFrame()
    for city in cities:
        df, _ = fetch_weather_data(city)
        if df is not None:
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df if not combined_df.empty else None


# Function to plot data for a single city
def plot_weather_data(df, city_name):
    fig = px.line(
        df,
        x="time",
        y="temp",
        color="name",
        title=f"Temperature Trends for {city_name}",
        labels={"time": "Time", "temp": "Temperature (°C)"},
        template="plotly_dark",
    )
    fig.show()


# Function to plot comparison chart
def plot_comparison_chart(cities):
    combined_df = fetch_weather_for_cities(cities)

    if combined_df is None:
        QMessageBox.warning(None, "Error", "No data available for the selected cities.")
        return

    fig = px.line(
        combined_df,
        x="time",
        y="temp",
        color="name",
        title="Temperature Comparison for Selected Cities",
        labels={"time": "Time", "temp": "Temperature (°C)", "name": "City"},
        template="plotly_dark",
    )
    fig.show()


# Main Window Class
class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather Data Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        # Set up the main layout and colors
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Add a header
        header_label = QLabel("Weather Viewer")
        header_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #1e88e5; padding: 10px;")
        main_layout.addWidget(header_label)

        # Dropdown for cities
        city_dropdown_layout = QHBoxLayout()
        city_label = QLabel("Select a City:")
        city_label.setFont(QFont("Helvetica", 14))
        self.city_dropdown = QComboBox()
        self.city_dropdown.addItems(
            [
                "Moscow",
                "Istanbul",
                "London",
                "Berlin",
                "Madrid",
                "Rome",
                "Paris",
                "Kiev",
                "Hamburg",
                "Warsaw",
                "Vienna",
                "Athene",
                "Saint Petersburg",
                "Lisbon",
                "Stockholm",
                "Budapest",
                "Copenhagen",
                "Milan",
                "Venice",
                "Pristina",
                "Florence",
            ]
        )
        self.city_dropdown.setFont(QFont("Helvetica", 14))
        self.city_dropdown.setStyleSheet("background-color: #e3f2fd; padding: 5px;")

        city_dropdown_layout.addWidget(city_label)
        city_dropdown_layout.addWidget(self.city_dropdown)
        main_layout.addLayout(city_dropdown_layout)

        # Display the latest data button
        self.display_button = QPushButton("Show Weather Data")
        self.display_button.setFont(QFont("Helvetica", 14))
        self.display_button.setStyleSheet(
            "background-color: #4caf50; color: white; padding: 10px; border-radius: 5px;"
        )
        self.display_button.clicked.connect(self.display_weather_data)
        main_layout.addWidget(self.display_button)

        # Multi-city comparison
        comparison_layout = QHBoxLayout()
        comparison_label = QLabel("Compare Cities (comma-separated):")
        comparison_label.setFont(QFont("Helvetica", 14))
        self.city_comparison_input = QLineEdit()
        self.city_comparison_input.setFont(QFont("Helvetica", 14))
        self.city_comparison_input.setStyleSheet("background-color: #fffde7; padding: 5px;")

        comparison_button = QPushButton("Compare Cities")
        comparison_button.setFont(QFont("Helvetica", 14))
        comparison_button.setStyleSheet(
            "background-color: #fbc02d; color: white; padding: 10px; border-radius: 5px;"
        )
        comparison_button.clicked.connect(self.compare_cities)

        comparison_layout.addWidget(comparison_label)
        comparison_layout.addWidget(self.city_comparison_input)
        comparison_layout.addWidget(comparison_button)
        main_layout.addLayout(comparison_layout)

        # Run external script button
        self.run_script_button = QPushButton("Run External Script (second.py)")
        self.run_script_button.setFont(QFont("Helvetica", 14))
        self.run_script_button.setStyleSheet(
            "background-color: #1976d2; color: white; padding: 10px; border-radius: 5px;"
        )
        self.run_script_button.clicked.connect(self.run_external_script)
        main_layout.addWidget(self.run_script_button)

    def display_weather_data(self):
        city_name = self.city_dropdown.currentText()
        df, latest_time = fetch_weather_data(city_name)
        if df is not None:
            QMessageBox.informa
