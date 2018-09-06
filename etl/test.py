from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import YouTube 

import json
import credentials

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
DEVELOPER_KEY = credentials.DEVELOPER_KEY

def youtube_search(keyword):
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
	response = youtube.search().list(
	    q=keyword,
	    part='id,snippet',
	    relevanceLanguage="en",
	    type="video",
	).execute()

	print(response)

def youtube_download(url):
	YouTube(url).streams.filter(subtype='mp4').first().download()


# youtube_search("Lord of the Rings official trailer")
youtube_download("http://youtube.com/watch?v=V75dMMIW2B4")

