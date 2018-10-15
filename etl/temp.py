import movie, commons
import pickle
from collections import defaultdict

movies = commons.load_movies()

print (len(movies)) # 198 movies


year_count = defaultdict(lambda: 0)
genre_count = defaultdict(lambda: 0)
for m in movies.values():
	year_count[m.imdb_features['year']] += 1
	for genre in m.imdb_features['genre']:
		genre_count[genre] += 1

year_count = [(year, year_count[year]) for year in year_count]
genre_count = [(genre, genre_count[genre]) for genre in genre_count]
print(sorted(year_count, key=lambda x: x[0]))
print(sorted(genre_count, key=lambda x: x[1], reverse=True))