"""
using pretrained VGG-Face with calibrated just face images
"""
import sklearn, keras, numpy, keras_vggface
from keras_vggface.vggface import VGGFace
import commons, os, pickle, random
import baseline

from datetime import datetime

VGGFACE_FACE_DIR = os.path.join(commons.FEATURES_DIR, "vggface_face")
TRAIN_X = "train_x.pickle"
TRAIN_Y = "train_y.pickle"
TEST_X = "test_x.pickle"
TEST_Y = "test_y.pickle"
TEST_WHO = "test_who.txt"
VGGFACE_MODEL = VGGFACE_FACE_DIR + 'model.joblib'

def generate_vggface_data():

	if not os.path.exists(commons.FEATURES_DIR):
		os.mkdir(commons.FEATURES_DIR)

	if not os.path.exists(VGGFACE_FACE_DIR):
		os.mkdir(VGGFACE_FACE_DIR)

	# if we already got them...
	generated = (
		os.path.exists(VGGFACE_FACE_DIR + '/' + TRAIN_X) and
		os.path.exists(VGGFACE_FACE_DIR + '/' + TRAIN_Y) and
		os.path.exists(VGGFACE_FACE_DIR + '/' + TEST_X) and
		os.path.exists(VGGFACE_FACE_DIR + '/' + TEST_Y) and
		os.path.exists(VGGFACE_FACE_DIR + '/' + TEST_WHO)
		)

	if generated:
		return

	print("Generating vgg_face_face features... ", datetime.now())
	train_ids = set([])
	with open(commons.TRAIN_FILE, 'r') as f:
		for line in f.readlines():
			train_ids.add(line.strip())

	test_ids = set([])
	with open(commons.TEST_FILE, 'r') as f:
		for line in f.readlines():
			test_ids.add(line.strip())

	train_x, train_y, test_x, test_y, test_who = [], [], [], [], []
	labelof = commons.get_label()

	count = 0
	for imdb_id in labelof:

		count += 1
		print("\r{}/{}...".format(count, len(labelof)), end='')
		characters = commons.get_characters(imdb_id)


		# for each character, pick random 5 encodings as its datapoint
		for i in range(len(characters)):
			for encoding in characters[i]:
				x = encoding.flatten()
				y = labelof[imdb_id][i]

			# character = random.sample(characters[i], 5)
			# x = numpy.array([ x.flatten() for x in character ])
			# x.flatten()
			# y = labelof[imdb_id][i]

			if imdb_id in train_ids:
				train_x.append(x)
				train_y.append(y)
			else:
				test_x.append(x)
				test_y.append(y)
				test_who.append("{}-{}-{}".format(imdb_id, i, 0))

	print("Done. ", datetime.now())

	with open(VGGFACE_FACE_DIR + '/' + TRAIN_X, 'wb') as f:
		pickle.dump(train_x, f)
	with open(VGGFACE_FACE_DIR + '/' + TRAIN_Y, 'wb') as f:
		pickle.dump(train_y, f)	
	with open(VGGFACE_FACE_DIR + '/' + TEST_X, 'wb') as f:
		pickle.dump(test_x, f)
	with open(VGGFACE_FACE_DIR + '/' + TEST_Y, 'wb') as f:
		pickle.dump(test_y, f)
	with open(VGGFACE_FACE_DIR + '/' + TEST_WHO, 'w') as f:
		for who in test_who:
			f.write("{}\n".format(who))

def load_training_data():
	generate_vggface_data()
	with open(VGGFACE_FACE_DIR + '/' + TRAIN_X, 'rb') as f:
		train_x = pickle.load(f)
	with open(VGGFACE_FACE_DIR + '/' + TRAIN_Y, 'rb') as f:
		train_y = pickle.load(f)
	return (train_x, train_y)

def load_test_data():
	generate_vggface_data()
	with open(VGGFACE_FACE_DIR + '/' + TEST_X, 'rb') as f:
		test_x = pickle.load(f)
	with open(VGGFACE_FACE_DIR + '/' + TEST_Y, 'rb') as f:
		test_y = pickle.load(f)
	with open(VGGFACE_FACE_DIR + '/' + TEST_WHO, 'r') as f:
		test_who = []
		for line in f.readlines():
			test_who.append(line.strip())
	return (test_x, test_y, test_who)


if __name__ == '__main__':
	baseline.train(data=load_training_data(), model_path=VGGFACE_MODEL)
	baseline.test(data=load_test_data(), model_path=VGGFACE_MODEL)