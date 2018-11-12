import sklearn, keras, numpy, keras_vggface
from keras_vggface.vggface import VGGFace
import commons, os, pickle
import baseline

from datetime import datetime

VGGFACE_DIR = os.path.join(commons.FEATURES_DIR, "vggface")
TRAIN_X = "train_x.pickle"
TRAIN_Y = "train_y.pickle"
TEST_X = "test_x.pickle"
TEST_Y = "test_y.pickle"
TEST_WHO = "test_who.txt"
VGGFACE_MODEL = VGGFACE_DIR + 'model.joblib'

def generate_vggface_data():
	if not os.path.exists(commons.FEATURES_DIR):
		os.mkdir(commons.FEATURES_DIR)

	if not os.path.exists(VGGFACE_DIR):
		os.mkdir(VGGFACE_DIR)

	# if we already got them...
	generated = (
		os.path.exists(VGGFACE_DIR + '/' + TRAIN_X) and
		os.path.exists(VGGFACE_DIR + '/' + TRAIN_Y) and
		os.path.exists(VGGFACE_DIR + '/' + TEST_X) and
		os.path.exists(VGGFACE_DIR + '/' + TEST_Y) and
		os.path.exists(VGGFACE_DIR + '/' + TEST_WHO)
		)

	if generated:
		return

	# generate them, save, and return them!
	train_ids = set([])
	with open(commons.TRAIN_FILE, 'r') as f:
		for line in f.readlines():
			train_ids.add(line.strip())

	test_ids = set([])
	with open(commons.TEST_FILE, 'r') as f:
		for line in f.readlines():
			test_ids.add(line.strip())

	# encoding and separate (data, label)
	train_x, train_y, test_x, test_y, test_who = [], [], [], [], []
	labelof = commons.get_label()

	IMAGE_SIZE = 224
	cnn_model = VGGFace(include_top=False, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3), pooling='None')
	print("Loading baseline data...", datetime.now())

	image_filenames = [x for x in sorted(os.listdir(commons.TRAIN_IMAGES_DIR)) if len(x) > 4 and x[-4:] == '.jpg']
	for i in range(len(image_filenames)):
		print("{}/{}...".format(i, len(image_filenames)), end='\r')

		image_filename = image_filenames[i]
		imdb_id, character_id, timestamp = image_filename[:-4].split('-')
		character_id = int(character_id)

		# if this movie is not yet labeled
		if imdb_id not in labelof:
			continue

		image = keras.preprocessing.image.load_img(
			os.path.join(commons.TRAIN_IMAGES_DIR, image_filename), 
			target_size=(IMAGE_SIZE, IMAGE_SIZE))

		x = keras.preprocessing.image.img_to_array(image)
		x = numpy.expand_dims(x, axis=0)
		x = keras_vggface.utils.preprocess_input(x, version=1)
		x = cnn_model.predict(x)

		y = labelof[imdb_id][character_id]

		if imdb_id in train_ids:
			train_x.append(x)
			train_y.append(y)
		else:
			test_x.append(x)
			test_y.append(y)
			test_who.append(image_filename[:-4])

	print("Done. ", datetime.now())

	with open(VGGFACE_DIR + '/' + TRAIN_X, 'wb') as f:
		pickle.dump(train_x, f)
	with open(VGGFACE_DIR + '/' + TRAIN_Y, 'wb') as f:
		pickle.dump(train_y, f)	
	with open(VGGFACE_DIR + '/' + TEST_X, 'wb') as f:
		pickle.dump(test_x, f)
	with open(VGGFACE_DIR + '/' + TEST_Y, 'wb') as f:
		pickle.dump(test_y, f)
	with open(VGGFACE_DIR + '/' + TEST_WHO, 'w') as f:
		for who in test_who:
			f.write("{}\n".format(who))

def load_training_data():
	generate_vggface_data()
	with open(VGGFACE_DIR + '/' + TRAIN_X, 'rb') as f:
		train_x = pickle.load(f)
	with open(VGGFACE_DIR + '/' + TRAIN_Y, 'rb') as f:
		train_y = pickle.load(f)
	return (train_x, train_y)

def load_test_data():
	generate_vggface_data()
	with open(VGGFACE_DIR + '/' + TEST_X, 'rb') as f:
		test_x = pickle.load(f)
	with open(VGGFACE_DIR + '/' + TEST_Y, 'rb') as f:
		test_y = pickle.load(f)
	with open(VGGFACE_DIR + '/' + TEST_WHO, 'r') as f:
		test_who = []
		for line in f.readlines():
			test_who.append(line.strip())
	return (test_x, test_y, test_who)


if __name__ == '__main__':
	baseline.train(data=load_training_data(), model_path=VGGFACE_MODEL)
	baseline.test(data=load_test_data(), model_path=VGGFACE_MODEL)