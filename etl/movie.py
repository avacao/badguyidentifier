from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import YouTube 

import json
import credentials

VIDEOS_PATH = "../data/videos"
CAPTIONS_PATH = "../data/captions"

class Movie:
	def __init__(self, name):
		# First tier features, from IMDB
		self.name = name
		self.imdb_features = {}
		self.imdb_id = None
		self.year = None
		self.genre = None

		# Second tier features, from YouTube
		self.video_id = "ue80QwXMRHg" #self._get_video_id()


	"""
	Uses YouTube API and search for movie trailer.
	We trust YouTube that the first result returned is the trailer we are looking for.
	"""
	def _get_video_id(self):
		youtube_api_service_name = 'youtube'
		youtube_api_version = 'v3'
		DEVELOPER_KEY = credentials.DEVELOPER_KEY

		keyword = self.name + " official trailer"

		youtube = build(youtube_api_service_name, youtube_api_version, developerKey=DEVELOPER_KEY)
		response = youtube.search().list(
			q=keyword,
			part='id',
			relevanceLanguage="en",
			type="video",
		).execute()

		return response['items'][0]['id']['videoId']

	"""
	Use video_id to download video and its caption from YouTuBe.
	"""
	def download(self):
		url = "https://www.youtube.com/watch?v=" + self.video_id

		y = YouTube(url)

		# download video
		y.streams.filter(subtype='mp4').first()\
			.download(output_path=VIDEOS_PATH, filename=self.video_id)

		# fetch caption
		caption = y.captions.get_by_language_code('en').generate_srt_captions()
		with open(CAPTIONS_PATH + "/{}.txt".format(self.video_id), 'w') as f:
			f.write(caption)

	def __str__(self):
		return "{}\t{}\t{}\t{}".format(self.name, self.video_id, self.year, self.genre)


m = Movie("thor ragnarok")
m.download()

