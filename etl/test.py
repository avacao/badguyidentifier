from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import credentials

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
DEVELOPER_KEY = credentials.DEVELOPER_KEY

print(DEVELOPER_KEY)

def youtube_search(keyword):
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
	response = youtube.search().list(
	    q=keyword,
	    part='id,snippet',
	    relevanceLanguage="en",
	    type="video",
	).execute()

	print(response)

# youtube_search("Lord of the Rings official trailer")

result = """{'nextPageToken': 'CAUQAA', 'items': [{'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/ui4Eq_wal5m4y_fvL4DQKrZgiwU"', 'id': {'videoId': 'V75dMMIW2B4', 'kind': 'youtube#video'}, 'snippet': {'liveBroadcastContent': 'none', 'channelTitle': 'Movieclips', 'channelId': 'UC3gNmTGu-TTbFPpfSs5kNkg', 'thumbnails': {'default': {'width': 120, 'height': 90, 'url': 'https://i.ytimg.com/vi/V75dMMIW2B4/default.jpg'}, 'medium': {'width': 320, 'height': 180, 'url': 'https://i.ytimg.com/vi/V75dMMIW2B4/mqdefault.jpg'}, 'high': {'width': 480, 'height': 360, 'url': 'https://i.ytimg.com/vi/V75dMMIW2B4/hqdefault.jpg'}}, 'title': 'The Lord of the Rings: The Fellowship of the Ring Official Trailer #1 - (2001) HD', 'publishedAt': '2011-09-02T09:01:51.000Z', 'description': 'The Lord of the Rings: The Fellowship of the Ring movie clips: http://j.mp/1CLwxex BUY THE MOVIE: http://bit.ly/2cqARtE Don't miss the HOTTEST NEW ..."}, 'kind': 'youtube#searchResult'}, {'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/P8PDHgiW-M0pM_IgjiMK3uzM3yQ"', 'id': {'videoId': 'r5X-hFf6Bwo', 'kind': 'youtube#video'}, 'snippet': {'liveBroadcastContent': 'none', 'channelTitle': 'Movieclips', 'channelId': 'UC3gNmTGu-TTbFPpfSs5kNkg', 'thumbnails': {'default': {'width': 120, 'height': 90, 'url': 'https://i.ytimg.com/vi/r5X-hFf6Bwo/default.jpg'}, 'medium': {'width': 320, 'height': 180, 'url': 'https://i.ytimg.com/vi/r5X-hFf6Bwo/mqdefault.jpg'}, 'high': {'width': 480, 'height': 360, 'url': 'https://i.ytimg.com/vi/r5X-hFf6Bwo/hqdefault.jpg'}}, 'title': 'The Lord of the Rings: The Return of the King Official Trailer #1 - (2003) HD', 'publishedAt': '2011-09-02T16:23:26.000Z', 'description': "LOTR: The Return of the King movie clips http://j.mp/y50cIO BUY THE MOVIE: http://bit.ly/2cEwgsB Don't miss the HOTTEST NEW TRAILERS: ..."}, 'kind': 'youtube#searchResult'}, {'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/E3bo-5f8k1Rl39HKGXkzRJNCPrY"', 'id': {'videoId': 'aStYWD25fAQ', 'kind': 'youtube#video'}, 'snippet': {'liveBroadcastContent': 'none', 'channelTitle': 'Movieclips', 'channelId': 'UC3gNmTGu-TTbFPpfSs5kNkg', 'thumbnails': {'default': {'width': 120, 'height': 90, 'url': 'https://i.ytimg.com/vi/aStYWD25fAQ/default.jpg'}, 'medium': {'width': 320, 'height': 180, 'url': 'https://i.ytimg.com/vi/aStYWD25fAQ/mqdefault.jpg'}, 'high': {'width': 480, 'height': 360, 'url': 'https://i.ytimg.com/vi/aStYWD25fAQ/hqdefault.jpg'}}, 'title': 'The Lord of the Rings: The Fellowship of the Ring Official Trailer #2 - (2001) HD', 'publishedAt': '2011-09-02T09:06:29.000Z', 'description': "The Lord of the Rings: The Fellowship of the Ring movie clips: http://j.mp/1CLwxex BUY THE MOVIE: http://bit.ly/2cqARtE Don't miss the HOTTEST NEW ..."}, 'kind': 'youtube#searchResult'}, {'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/TtuCq2PHQoDOFte1zqTIUziNdRc"', 'id': {'videoId': 'LbfMDwc4azU', 'kind': 'youtube#video'}, 'snippet': {'liveBroadcastContent': 'none', 'channelTitle': 'Movieclips Classic Trailers', 'channelId': 'UCTCjFFoX1un-j7ni4B6HJ3Q', 'thumbnails': {'default': {'width': 120, 'height': 90, 'url': 'https://i.ytimg.com/vi/LbfMDwc4azU/default.jpg'}, 'medium': {'width': 320, 'height': 180, 'url': 'https://i.ytimg.com/vi/LbfMDwc4azU/mqdefault.jpg'}, 'high': {'width': 480, 'height': 360, 'url': 'https://i.ytimg.com/vi/LbfMDwc4azU/hqdefault.jpg'}}, 'title': 'The Lord of the Rings: The Two Towers (2002) Official Trailer #2 - Orlando Bloom Movie HD', 'publishedAt': '2014-05-15T03:53:35.000Z', 'description': 'Subscribe to CLASSIC TRAILERS: http://bit.ly/1u43jDe Subscribe to TRAILERS: http://bit.ly/sxaw6h Subscribe to COMING SOON: http://bit.ly/H2vZUn Like us on ...'}, 'kind': 'youtube#searchResult'}, {'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/4DE-8AcFLB41OWqfLr-r_r2aBt8"', 'id': {'videoId': '-JNVtorI3vw', 'kind': 'youtube#video'}, 'snippet': {'liveBroadcastContent': 'none', 'channelTitle': 'Movieclips Classic Trailers', 'channelId': 'UCTCjFFoX1un-j7ni4B6HJ3Q', 'thumbnails': {'default': {'width': 120, 'height': 90, 'url': 'https://i.ytimg.com/vi/-JNVtorI3vw/default.jpg'}, 'medium': {'width': 320, 'height': 180, 'url': 'https://i.ytimg.com/vi/-JNVtorI3vw/mqdefault.jpg'}, 'high': {'width': 480, 'height': 360, 'url': 'https://i.ytimg.com/vi/-JNVtorI3vw/hqdefault.jpg'}}, 'title': 'The Lord of the Ring Trilogy (2001-2003) Official Supertrailer - Elijah Wood, Ian McKellan Movie HD', 'publishedAt': '2014-05-15T04:11:23.000Z', 'description': 'Subscribe to CLASSIC TRAILERS: http://bit.ly/1u43jDe Subscribe to TRAILERS: http://bit.ly/sxaw6h Subscribe to COMING SOON: http://bit.ly/H2vZUn Like us on ...'}, 'kind': 'youtube#searchResult'}], 'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/aOxXi0xwIa4ODklFSpT-jko84gc"', 'pageInfo': {'resultsPerPage': 5, 'totalResults': 1000000}, 'regionCode': 'US', 'kind': 'youtube#searchListResponse'}"""
result = result.replace("\"", "\\\"")
result = result.replace("'", "\"")

print(result)
parsed = json.loads(result)
print(json.dump(parsed, indent=4))