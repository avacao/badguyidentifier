import os, pickle

DATA_DIR = "../data/"

MOVIES_PATH = DATA_DIR + "keyvalue.pkl"

VIDEO_DIR = DATA_DIR + "videos/"
CAPTION_DIR = DATA_DIR + "captions/"
FACES_DIR = DATA_DIR + "faces/"

"""
Returns: dictionary {imdb_id -> movie object}
"""
def load_movies():
	if os.path.exists(MOVIES_PATH):
		with open(MOVIES_PATH, 'rb') as f:
			movies = pickle.load(f)
	else:
		movies = {}
	return movies # imdb_id -> movie object


def get_video_path(imdb_id):
	return VIDEO_DIR + imdb_id + '.mp4'

"""
Return faces directory of this movie. 
Create if not exists.
"""
def get_faces_dir(imdb_id):
	ret = FACES_DIR + imdb_id + '/'

	if not os.path.isdir(ret):
		os.mkdir(ret)

	return ret