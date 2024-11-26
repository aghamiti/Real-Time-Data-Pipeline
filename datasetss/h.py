import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('weather_data.db')

# Query the data into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM weather_data", conn)

# Display the DataFrame
print(df)

# Close the connection
conn.close()
