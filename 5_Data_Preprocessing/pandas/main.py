import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
url = "https://raw.githubusercontent.com/justmarkham/pandas-videos/master/data/imdb_1000.csv"
df = pd.read_csv(url)

# Display first few rows
print(df.head())

# Print column names to identify the correct column name for the release year
print(df.columns)

# Top 10 highest-rated movies
top_movies = df[['title', 'star_rating']].sort_values(by='star_rating', ascending=False).head(10)
print("\nTop 10 Highest-Rated Movies:\n", top_movies)

# Count movies by genre
df['genre'] = df['genre'].apply(lambda x: x.split(',')[0])  # Take first genre if multiple
genre_counts = df['genre'].value_counts()

# Plot genres
plt.figure(figsize=(10,5))
genre_counts.head(10).plot(kind='bar', color='skyblue')
plt.title("Top 10 Movie Genres in IMDb Dataset")
plt.xlabel("Genre")
plt.ylabel("Number of Movies")
plt.xticks(rotation=45)
plt.show()

# Trend of movie durations
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
df.groupby('duration').size().plot(kind='line', figsize=(10,5), color='red', marker='o')
plt.title("Trend of Movie Durations")
plt.xlabel("Duration (minutes)")
plt.ylabel("Number of Movies")
plt.grid()
plt.show()