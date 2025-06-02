import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
df = pd.read_csv(url)

# Select relevant columns
df = df[['location', 'date', 'total_cases', 'total_deaths', 'new_cases', 'new_deaths']]
df['date'] = pd.to_datetime(df['date'])

# Select data for a specific country
country = "United States"
df_country = df[df['location'] == country]

# Plot new cases over time
plt.figure(figsize=(10,5))
plt.plot(df_country['date'], df_country['new_cases'], label="New Cases", color='red', alpha=0.7)
plt.title(f"Daily New COVID-19 Cases in {country}")
plt.xlabel("Date")
plt.ylabel("Number of Cases")
plt.legend()
plt.grid()
plt.show()

# Calculate Case Fatality Rate (CFR)
df_country['CFR'] = (df_country['total_deaths'] / df_country['total_cases']) * 100

# Plot Case Fatality Rate over time
plt.figure(figsize=(10,5))
plt.plot(df_country['date'], df_country['CFR'], label="Case Fatality Rate (%)", color='purple')
plt.title(f"COVID-19 Case Fatality Rate in {country}")
plt.xlabel("Date")
plt.ylabel("Fatality Rate (%)")
plt.legend()
plt.grid()
plt.show()