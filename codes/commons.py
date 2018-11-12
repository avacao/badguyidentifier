import os, pickle
import face_recognition
from collections import defaultdict

DATA_DIR = "../data/"

MOVIES_PATH = DATA_DIR + "keyvalue.pkl"

VIDEO_DIR = DATA_DIR + "videos/"
CAPTION_DIR = DATA_DIR + "captions/"
FACES_DIR = DATA_DIR + "faces/"

IMAGE_DIR = DATA_DIR + "images/"
IMAGE_DONE_DIR = IMAGE_DIR + '_DONE/'

TRAIN_IMAGES_DIR = DATA_DIR + "train_images/"
TRAIN_IMAGES_DONE_DIR = TRAIN_IMAGES_DIR + '_DONE/'

TRAIN_FILE = DATA_DIR + "train.txt"
TEST_FILE = DATA_DIR + "test.txt"

BASELINE_DIR = DATA_DIR + "baseline/"
BASELINE_MODEL = BASELINE_DIR + 'model.joblib'
BASELINE_TRAIN_X = BASELINE_DIR + 'train_x.pickle'
BASELINE_TRAIN_Y = BASELINE_DIR + 'train_y.pickle'
BASELINE_TEST_X = BASELINE_DIR + 'test_x.pickle'
BASELINE_TEST_Y = BASELINE_DIR + 'test_y.pickle'
BASELINE_TEST_WHO = BASELINE_DIR + 'test_who.txt'

FEATURES_DIR = os.path.join(DATA_DIR, "features")

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

def create_images_dir_if_not_exists():
	if not os.path.exists(IMAGE_DIR):
		os.mkdir(IMAGE_DIR)

	if not os.path.exists(IMAGE_DONE_DIR):
		os.mkdir(IMAGE_DONE_DIR)


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

"""
Returns a list, where index i = [ face_recognition encodings ] of character i
"""
def get_characters(imdb_id):
	import ast

	face_dir = get_faces_dir(imdb_id)

	# check if directory exists and face cluster is done
	if not (os.path.exists(face_dir) and os.path.exists(os.path.join(face_dir, '_SUCCESS'))):
		raise RuntimeError("movie <{}> {} face_dir / _SUCCESS not exists.".format(imdb_id, movies[imdb_id].name))

	character_indices = [] 

	with open(os.path.join(face_dir, '_SUCCESS'), 'r') as f:
		for line in f.readlines():
			if len(line) > 0 and line[0] != '#':
				character_indices.append( ast.literal_eval( line.split(':')[1].strip() ))

	faces = open_faces_of_movie(imdb_id)

	characters = []
	for i in range(len(character_indices)):
		encodings = []
		for number in character_indices[i]:
			try:
				encodings.append( face_recognition.face_encodings(faces[number])[0] )
			except IndexError: # face not found
				continue
		characters.append(encodings)

	return characters

"""
return a dictionary : imdb_id -> character_id -> LABEL
"""
def get_label():
	movies = load_movies()
	labelof = defaultdict(dict)
	labelset = set(['GOOD','BAD','N','NA'])

	for imdb_id in movies:
		for label_file in ['_LABEL{}'.format(i) for i in range(1,4)]:

			if os.path.exists(os.path.join(FACES_DIR, imdb_id + '/' + label_file)):
				with open(os.path.join(FACES_DIR, imdb_id + '/' + label_file), 'r') as f:
					for line in f.readlines():
						if len(line) > 2:
							character_id, label = line.strip().split(':')
							character_id = int(character_id)

							# corner case
							if len(label) > 6 and label[:6] == "SAMEAS":
								labelof[imdb_id][character_id] = labelof[imdb_id][int(label[6:])]
							else:
								labelof[imdb_id][character_id] = label

							assert(labelof[imdb_id][character_id] in labelset)
				break

	return labelof