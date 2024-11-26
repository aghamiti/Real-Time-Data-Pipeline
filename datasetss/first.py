import pandas as pd
import numpy as np
import datetime
import requests

import json
import csv
from datetime import datetime, timedelta, timezone

import sqlite3
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()


full_data = []
myapi = 'd45828935f9550d9d4aab319e95f8a67'

cityList = ["Moscow", "Istanbul", "London", "Berlin", "Madrid", "Rome", "Paris", "Kiev", "Hamburg", "Warsaw", "Vienna",
            "Athene", "Saint Petersburg", "Lisbon", "Stockholm", "Budapest", "Copenhagen","Milano","Venice"]
for city in cityList:
  response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={myapi}')
  data = response.json()
  temp_list = []
  temp_list.append(datetime.now())
  temp_list.append(data["id"])
  temp_list.append(data["name"])
  temp_list.append(data['timezone'])
  temp_list.append(data['sys']['country'])
  temp_list.append(data['weather'][0]['description'])
  temp_list.append(data["main"]['temp'])
  temp_list.append(data['main']['feels_like'])
  temp_list.append(data['main']['temp_min'])
  temp_list.append(data['main']['temp_max'])
  data['sys']['sunset'] = (datetime.fromtimestamp(data['sys']['sunset'])).strftime('%H:%M:%S')
  data['sys']['sunrise'] = (datetime.fromtimestamp(data['sys']['sunrise'])).strftime('%H:%M:%S')

  temp_list.append(data['sys']['sunrise'])
  temp_list.append(data['sys']['sunset'])
  temp_list.append(data['main']['humidity'])
  temp_list.append(data['wind']['speed'])

  full_data.append(temp_list)

columns = ['time', 'id', 'name', 'timezone', 'country', 'weather type', 'temp', 'feels like', 'temp_min', 'temp_max',
           'sunrise', 'sunset', 'humidity', 'speed']
df = pd.DataFrame(data=full_data, columns=columns)
df['time'] = pd.to_datetime(df['time'])
# drop duplicates
df = df.drop_duplicates()
# convert temperatures in celcius
col_list = ['temp', 'feels like', 'temp_min', 'temp_max']


def temperature_conv(df, col_list):
  for col in col_list:
    df[col] = df[col] - 273.15


temperature_conv(df, col_list)
temperatures = ['temp', 'feels like', 'temp_min', 'temp_max']


def round_temp(df, col_list):
  for col in col_list:
    df[col] = np.round(df[col])


round_temp(df, temperatures)
#
#
#
# connect to sql

