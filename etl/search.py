import requests
from bs4 import BeautifulSoup 

from movie import Movie

from collections import defaultdict



"""
Given a movie's imdb_id, determine if it's good for our project.
Returns: boolean
Logic: 
- must be English
- is not Animation
- votes >= 250,000
"""
def this_movie_ok(imdb_id):
	imdb_url = "https://www.imdb.com/title/" + imdb_id

	response = requests.get(imdb_url)
	if response.status_code != 200:
		print("\n\nError: movie with id {} failed to load from imdb\n\n".format(imdb_id))
		return False

	html = BeautifulSoup(response.content, 'html.parser')

	# get genres
	genres = []
	for line in html.find("div", class_="subtext").find_all("a")[:-1]:
		genres.append(line.contents[0])
	print(genres)

def get_movies_from_imdb():
	movies = defaultdict(list) # year -> a list of movie objects

	for year in range(2000, 2001):
		# 1. get most featured movies in this year from imdb
		imdb_list_url = "https://www.imdb.com/search/title?year={}&title_type=feature&".format(year)

		response = requests.get(imdb_list_url)
		if response.status_code != 200:
			print("\n\nError: year {} failed with status_code {}.\n\n".format(year, response.status_code))
			continue

		# 2. parse html response, get each movie
		html = BeautifulSoup(response.content, 'html.parser')
		for line in html.find_all("h3", class_="lister-item-header")[:20]:
			name, imdb_suburl = line.find('a').contents[0], line.find('a')['href']
			imdb_id = imdb_suburl.split('/')[2]
			print(name, imdb_id)

if __name__ == "__main__":
	this_movie_ok("tt0468569")
	#get_movies_from_imdb()


