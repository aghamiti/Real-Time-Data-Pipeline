import pandas as pd
import numpy as np
import datetime
import requests
import sqlite3
from datetime import datetime, timedelta, timezone

# Connect to SQLite database (it will create the database if it doesn't exist)
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Create the table in SQLite if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_data (
    time TEXT,
    id INTEGER,
    name TEXT,
    timezone INTEGER,
    country TEXT,
    weather_type TEXT,
    temp REAL,
    feels_like REAL,
    temp_min REAL,
    temp_max REAL,
    sunrise TEXT,
    sunset TEXT,
    humidity INTEGER,
    wind_speed REAL
);
''')

full_data = []
myapi = 'd45828935f9550d9d4aab319e95f8a67'

cityList = ["Moscow", "Istanbul", "London", "Berlin", "Madrid", "Rome", "Paris", "Kiev", "Hamburg", "Warsaw", "Vienna",
            "Athene", "Saint Petersburg", "Lisbon", "Stockholm", "Budapest", "Copenhagen","Milan","Venice","Pristina","Florence"]

# Fetch weather data for each city
for city in cityList:
  response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={myapi}')
  data = response.json()
  temp_list = []

  # Populate temp_list with weather data
  temp_list.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # Convert datetime to string
  temp_list.append(data["id"])  # City ID
  temp_list.append(data["name"])  # City name
  temp_list.append(data['timezone'])  # Timezone
  temp_list.append(data['sys']['country'])  # Country code
  temp_list.append(data['weather'][0]['description'])  # Weather description
  temp_list.append(data["main"]['temp'])  # Temperature in Kelvin
  temp_list.append(data['main']['feels_like'])  # Feels like temperature in Kelvin
  temp_list.append(data['main']['temp_min'])  # Min temperature in Kelvin
  temp_list.append(data['main']['temp_max'])  # Max temperature in Kelvin

  # Convert sunset and sunrise to readable time format (string)
  temp_list.append(datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'))
  temp_list.append(datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'))

  temp_list.append(data['main']['humidity'])  # Humidity
  temp_list.append(data['wind']['speed'])  # Wind speed

  full_data.append(temp_list)

# Convert the data to a pandas DataFrame
columns = ['time', 'id', 'name', 'timezone', 'country', 'weather_type', 'temp', 'feels_like', 'temp_min', 'temp_max',
           'sunrise', 'sunset', 'humidity', 'wind_speed']
df = pd.DataFrame(data=full_data, columns=columns)

# Convert 'time' column to string format
df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')

# Drop duplicate rows
df = df.drop_duplicates()

# Convert temperatures from Kelvin to Celsius
col_list = ['temp', 'feels_like', 'temp_min', 'temp_max']


def temperature_conv(df, col_list):
  for col in col_list:
    df[col] = df[col] - 273.15


temperature_conv(df, col_list)

# Round temperatures to the nearest integer
temperatures = ['temp', 'feels_like', 'temp_min', 'temp_max']


def round_temp(df, col_list):
  for col in col_list:
    df[col] = np.round(df[col])


round_temp(df, temperatures)

# Insert data into SQLite database
for index, row in df.iterrows():
  cursor.execute('''
    INSERT INTO weather_data (time, id, name, timezone, country, weather_type, temp, feels_like, temp_min, temp_max, sunrise, sunset, humidity, wind_speed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
    row['time'],  # Now a string (datetime in string format)
    row['id'],
    row['name'],
    row['timezone'],
    row['country'],
    row['weather_type'],
    row['temp'],
    row['feels_like'],
    row['temp_min'],
    row['temp_max'],
    row['sunrise'],
    row['sunset'],
    row['humidity'],
    row['wind_speed']
  ))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Data has been successfully inserted into the database.")
