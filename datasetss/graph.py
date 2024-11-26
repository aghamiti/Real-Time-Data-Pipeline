import sqlite3
import pandas as pd
import plotly.express as px


def plot_weather_data(city_list):
  # Connect to SQLite database
  conn = sqlite3.connect('weather_data.db')

  # Query the data into a pandas DataFrame, filtering by selected cities
  city_str = "','".join(city_list)  # Convert list of cities to a string for SQL query
  query = f"SELECT * FROM weather_data WHERE name IN ('{city_str}')"
  df = pd.read_sql_query(query, conn)

  # Close the connection
  conn.close()

  # Convert 'time' column to datetime for easier plotting
  df['time'] = pd.to_datetime(df['time'])

  # List of temperature columns to plot
  temperature_columns = ['temp', 'feels_like', 'temp_min', 'temp_max']
  labels = ['Temperature', 'Feels Like', 'Min Temperature', 'Max Temperature']

  for i, col in enumerate(temperature_columns):
    # Plot data for each temperature type
    fig = px.line(df, x='time', y=col, color='name',
                  title=f'{labels[i]} vs Time',
                  labels={col: f'{labels[i]} (°C)', 'time': 'Time'},
                  template='plotly_dark')  # You can change 'plotly_dark' to another theme

    # Customize the plot further
    fig.update_layout(
      xaxis_title='Time',
      yaxis_title=f'{labels[i]} (°C)',
      legend_title="Cities",
      hovermode='x unified'
    )

    # Show the plot
    fig.show()


# Example usage: Filter by specific cities
selected_cities = ["Moscow", "Istanbul", "London"]
plot_weather_data(selected_cities)

# import sqlite3
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# def plot_weather_data(city_list):
#   # Connect to SQLite database
#   conn = sqlite3.connect('weather_data.db')
#
#   # Query the data into a pandas DataFrame, filtering by selected cities
#   city_str = "','".join(city_list)  # Convert list of cities to a string for SQL query
#   query = f"SELECT * FROM weather_data WHERE name IN ('{city_str}')"
#   df = pd.read_sql_query(query, conn)
#
#   # Close the connection
#   conn.close()
#
#   # Convert 'time' column to datetime for easier plotting
#   df['time'] = pd.to_datetime(df['time'])
#
#   # Plot temperature (actual, feels like, min, max) for the filtered cities
#   temperature_columns = ['temp', 'feels_like', 'temp_min', 'temp_max']
#   labels = ['Temperature', 'Feels Like', 'Min Temperature', 'Max Temperature']
#
#   for i, col in enumerate(temperature_columns):
#     plt.figure(figsize=(10, 5))
#
#     # Plot data for each city
#     for city in city_list:
#       city_data = df[df['name'] == city]
#       plt.plot(city_data['time'], city_data[col], label=city, marker='o')
#
#     # Customize the plot
#     plt.title(f'{labels[i]} vs Time')
#     plt.xlabel('Time')
#     plt.ylabel(f'{labels[i]} (°C)')
#     plt.legend(title="Cities")
#     plt.grid(True)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#
#     # Show the plot
#     plt.show()
#
#
# # Example usage: Filter by specific cities
# selected_cities = ["Moscow", "Istanbul", "London"]
# plot_weather_data(selected_cities)
