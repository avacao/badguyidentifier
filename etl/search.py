import requests
from bs4 import BeautifulSoup 
import pickle, os.path

from movie import Movie

KEYVALUE_STORE_PATH = "../data/keyvalue.pkl"

def load_keyvalue_store():
	if os.path.exists(KEYVALUE_STORE_PATH):
		with open(KEYVALUE_STORE_PATH, 'rb') as f:
			movies = pickle.load(f)
	else:
		movies = {}
	return movies # imdb_id -> movie object

def save_movies(movies):
	with open(KEYVALUE_STORE_PATH, 'wb') as f:
		pickle.dump(movies, f, pickle.HIGHEST_PROTOCOL)

"""
Given a movie's imdb_id, determine if it's good for our project.
If yes, insert into our movies key-value store.
Return: boolean
Logic: 
- is not an animation
- must be in English
- votes >= 250,000
"""
def insert_if_ok(movies, name, imdb_id):
	imdb_url = "https://www.imdb.com/title/" + imdb_id

	response = requests.get(imdb_url)
	if response.status_code != 200:
		print("\n\nError: movie with id {} failed to load from imdb\n\n".format(imdb_id))
		return False

	html = BeautifulSoup(response.content, 'html.parser')

	# get genres
	genres = []
	for line in html.find("div", class_="subtext").find_all("a")[:-1]:
		genres.append(str(line.contents[0]))
	if "Animation" in set(genres):
		return False

	# get language
	languages = []
	for line in list(html.find("div", id="titleDetails").children)[9].find_all('a'):
		languages.append(str(line.contents[0]))
	if "English" not in languages:
		return False

	# get number of votes
	count = int(html.find("div", class_="imdbRating").find('a').find("span")\
			.contents[0].replace(',', ''))
	if count < 250000:
		return False

	if imdb_id not in movies:
		movies[imdb_id] = Movie(name, imdb_id)
		movies[imdb_id].imdb_features['genre'] = genres

	return True


def get_movies_from_imdb(movies):

	for year in range(2002, 2018):
		# 1. get most featured movies in this year from imdb
		imdb_list_url = "https://www.imdb.com/search/title?year={}&title_type=feature&".format(year)

		response = requests.get(imdb_list_url)
		if response.status_code != 200:
			print("\n\nError: year {} failed with status_code {}.\n\n".format(year, response.status_code))
			continue

		# 2. parse html response, get each movie
		html = BeautifulSoup(response.content, 'html.parser')
		for line in html.find_all("h3", class_="lister-item-header")[:20]:
			name, imdb_suburl = str(line.find('a').contents[0]), line.find('a')['href']
			imdb_id = imdb_suburl.split('/')[2]

			print("Movie {}...".format(name), end="")
			
			if insert_if_ok(movies, name, imdb_id):
				movies[imdb_id].imdb_features['year'] = year
				print("stored.")
			else:
				print("skipped.")

def download_movies(movies):
	for movie in movies.values():
		movie_path = "../data/videos/" + movie.imdb_id + ".mp4"
		if not os.path.isfile(movie_path):
			movie.download()

if __name__ == "__main__":
	movies = load_keyvalue_store()
	# get_movies_from_imdb(movies)
	# save_movies(movies)

	download_movies(movies)

