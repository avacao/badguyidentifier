## Dataset Generation
### Movie trailer scraping
Our movie trailer dataset is based on IMDB's featured films each year (see URL: https://www.imdb.com/search/title?year=2017&title_type=feature&). We scraped top 20 films from this webpage, and filter the results by the following rules:

1. No animated films.
2. The movie should (primarily) be in English.
3. Number of voters for the movie should exceed 250,000. [see TODO1]

[TODO1] Here a sense of scale is needed. Perhaps add a distribution of votes of top 20 films each year.
  
To start with, we limited our search to movies released between year 2000 and 2017, and ended with 198 movies with their IMDB title id as the primary key in our dataset, and year and genre as supporting features.

We then turn to YouTube to search for each movie's trailer given its title. We first incorporate Google's YouTube API to get search results using the following query: "\<movie_title> official trailer" and got a list of video URLs. We assumes that the first search result is what we want. In practice this assumption works very well and [TODO2] percent of videos returned are exactly what we want. We then use a python package, `pytube` to download the video in highest resolution given its URL.

The pipeline is completely automated and the whole process takes less than 15 minutes to complete, from scarping to downloading.


### Face recognition and comparsion