import sklearn, keras, numpy, keras_vggface
from keras_vggface.vggface import VGGFace
import os, random, pickle
import commons, audio_model, baseline, scene_model
from datetime import datetime

FUSION_DIR = os.path.join(commons.FEATURES_DIR, 'fusion')
FUSION_TRAIN_X = os.path.join(FUSION_DIR, 'train_x.pickle')
FUSION_TRAIN_Y = os.path.join(FUSION_DIR, 'train_y.pickle')
FUSION_TRAIN_WHO = os.path.join(FUSION_DIR, 'train_who.txt')
FUSION_TEST_X = os.path.join(FUSION_DIR, 'test_x.pickle')
FUSION_TEST_Y = os.path.join(FUSION_DIR, 'test_y.pickle')
FUSION_TEST_WHO = os.path.join(FUSION_DIR, 'test_who.txt')
FUSION_MODEL = os.path.join(FUSION_DIR, 'model.joblib')

NUM_IMAGES_USED = 2

def generate_fusion_data():
	if not os.path.exists(FUSION_DIR):
		os.mkdir(FUSION_DIR)

	if (os.path.exists(FUSION_TRAIN_X) and os.path.exists(FUSION_TRAIN_Y) and
		os.path.exists(FUSION_TRAIN_WHO) and os.path.exists(FUSION_TEST_X) and
		os.path.exists(FUSION_TEST_Y) and os.path.exists(FUSION_TEST_WHO)):
		with open(FUSION_TRAIN_X, 'rb') as f:
			train_x = pickle.load(f)
		with open(FUSION_TRAIN_Y, 'rb') as f:
			train_y = pickle.load(f)
		with open(FUSION_TRAIN_WHO, 'r') as f:
			train_who = []
			for line in f.readlines():
				train_who.append(line.strip())	
		with open(FUSION_TEST_X, 'rb') as f:
			test_x = pickle.load(f)
		with open(FUSION_TEST_Y, 'rb') as f:
			test_y = pickle.load(f)
		with open(FUSION_TEST_WHO, 'r') as f:
			test_who = []
			for line in f.readlines():
				test_who.append(line.strip())
		return (train_x, train_y, train_who), (test_x, test_y, test_who)

	audio_train_data = audio_model.load_training_data()
	audio_test_data = audio_model.load_test_data()

	train_ids, test_ids = commons.get_train_and_test_imbd_ids()
	movies, labelof = commons.load_movies(), commons.get_label()

	train_x, train_y, test_x, test_y = [], [], [], []
	train_who, test_who = audio_train_data[2], audio_test_data[2]

	IMAGE_SIZE = 224
	cnn_model = VGGFace(include_top=False, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3), pooling='None')
	vgg19_model = scene_model.VGG_19()

	print("Generating & merging features...", datetime.now())

	for (xs, ys, whos) in [audio_train_data, audio_test_data]:
		assert(len(xs) == len(ys) and len(ys) == len(whos))

		for i in range(len(whos)):
			print("\r{}/{}".format(i, len(whos)), end="")

			imdb_id, c_id, scene = whos[i].strip().split('-')
			start_time, end_time = scene.split('~')
			c_id, start_time, end_time = int(c_id), float(start_time), float(end_time)

			audio_x, y = numpy.asarray(xs[i]).flatten(), ys[i]

			# find 2 random images belonging to (imdb_id, c_id) scene
			images = [ x for x in os.listdir(commons.TRAIN_IMAGES_DIR) if 
						x.startswith("{}-{}".format(imdb_id, c_id)) ]
			temp_images = []

			for image in images:
				assert(image[-4:] == '.jpg')
				_, _, timestamp = image[:-4].split('-')
				timestamp = float(timestamp)
				if start_time <= timestamp and timestamp <= end_time:
					temp_images.append(image)

			assert(len(temp_images) >= 5) # a scene is guaranteed to have >= 5 images
			images = random.sample(temp_images, NUM_IMAGES_USED)

			image_x = []
			for image in images:
				image_filename = os.path.join(commons.TRAIN_IMAGES_DIR, image)
				image = keras.preprocessing.image.load_img(image_filename, 
					target_size=(IMAGE_SIZE, IMAGE_SIZE))

				# face features
				x = keras.preprocessing.image.img_to_array(image)
				x = numpy.expand_dims(x, axis=0)
				x = keras_vggface.utils.preprocess_input(x, version=1)
				x = cnn_model.predict(x)
				x = x.flatten()
				image_x.append(x)

				# scene features
				x = scene_model.extract_scene_feature(vgg19_model, image)
				x = x.flatten()
				image_x.append(x)

			x = numpy.concatenate(tuple(image_x + [audio_x]))

			if imdb_id in train_ids:
				train_x.append(x)
				train_y.append(y)
			elif imdb_id in test_ids:
				test_x.append(x)
				test_y.append(y)

	print("\rDone. ", datetime.now())

	with open(FUSION_TRAIN_X, 'wb') as f:
		pickle.dump(train_x, f)
	with open(FUSION_TRAIN_Y, 'wb') as f:
		pickle.dump(train_y, f)	
	with open(FUSION_TRAIN_WHO, 'w') as f:
		for who in train_who:
			f.write("{}\n".format(who))
	with open(FUSION_TEST_X, 'wb') as f:
		pickle.dump(test_x, f)
	with open(FUSION_TEST_Y, 'wb') as f:
		pickle.dump(test_y, f)
	with open(FUSION_TEST_WHO, 'w') as f:
		for who in test_who:
			f.write("{}\n".format(who))

	return (train_x, train_y, train_who), (test_x, test_y, test_who)


if __name__ == '__main__':
	train_data, test_data = generate_fusion_data()

	# exclude N, N/A from data
	print("before, len train, test:", len(train_data[0]), len(test_data[0]))
	for i in range(len(train_x) - 1, -1, -1):
		if train_y[i] == "NA" or train_y[i] == 'N':
			train_x.pop(i)
			train_y.pop(i)
			train_who.pop(i)

	for i in range(len(train_x) - 1, -1, -1):
		if train_y[i] == "NA" or train_y[i] == 'N':
			train_x.pop(i)
			train_y.pop(i)
			train_who.pop(i)
	print("after, len train, test:", len(train_data[0]), len(test_data[0]))

	baseline.train(data=train_data, model_path=FUSION_MODEL)
	baseline.test(data=test_data, model_path=FUSION_MODEL)
