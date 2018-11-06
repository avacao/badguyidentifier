import os, pickle
import face_recognition

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

def get_characters_path(imdb_id):
	return os.path.join(FACES_DIR, imdb_id + '/characters.pickle')

def get_characters(imdb_id):
	if os.path.exists(get_characters_path(imdb_id)):
		with open(get_characters_path(imdb_id), 'rb') as f:
			characters = pickle.load(f)
			return characters
	else:
		raise RuntimeError("movie <{}> does not have face encodings generated".format(imdb_id))
"""
Return: a dictionary : face file index as int -> face_recognition image
"""
def open_faces_of_movie(imdb_id):
	movies = load_movies()
	movie = movies[imdb_id]
	face_dir = get_faces_dir(imdb_id)

	# check if face detection has succeeded
	if not os.path.exists(os.path.join(face_dir, '_SUCCESS')):
		raise RuntimeError("ERROR: movie <{}> {} face not extracted.".format(imdb_id, movie.name))

	# open all faces
	# NOTE: maybe keep file sequence to use heuistics?
	faces = {} # integer of filename -> face image
	for file in os.listdir(face_dir):
		filename, extension = os.path.splitext(file)
		if extension == ".jpg":
				faces[int(filename)] = face_recognition.load_image_file(os.path.join(face_dir, file))

	return faces

