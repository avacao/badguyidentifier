import sklearn, keras
from keras.applications import vgg16
import numpy 
from sklearn.svm import SVC

import os, commons, pickle
from datetime import datetime
from collections import defaultdict

"""
baseline data:
image features come from the last non-fully-connected layer of vgg16.
Only load images from labeled movies!!!
"""
def generate_baseline_data():
	if not os.path.exists(commons.BASELINE_DIR):
		os.mkdir(commons.BASELINE_DIR)

	# if we already got them...
	generated = (
		os.path.exists(commons.BASELINE_TRAIN_X) and
		os.path.exists(commons.BASELINE_TRAIN_Y) and
		os.path.exists(commons.BASELINE_TEST_X) and
		os.path.exists(commons.BASELINE_TEST_Y) and
		os.path.exists(commons.BASELINE_TEST_WHO)
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
	cnn_model = vgg16.VGG16(weights='imagenet', include_top=False)
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
		x = vgg16.preprocess_input(x)
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

	with open(commons.BASELINE_TRAIN_X, 'wb') as f:
		pickle.dump(train_x, f)
	with open(commons.BASELINE_TRAIN_Y, 'wb') as f:
		pickle.dump(train_y, f)	
	with open(commons.BASELINE_TEST_X, 'wb') as f:
		pickle.dump(test_x, f)
	with open(commons.BASELINE_TEST_Y, 'wb') as f:
		pickle.dump(test_y, f)
	with open(commons.BASELINE_TEST_WHO, 'w') as f:
		for who in test_who:
			f.write("{}\n".format(who))


def load_training_data():
	generate_baseline_data()
	with open(commons.BASELINE_TRAIN_X, 'rb') as f:
		train_x = pickle.load(f)
	with open(commons.BASELINE_TRAIN_Y, 'rb') as f:
		train_y = pickle.load(f)
	return train_x, train_y

def load_test_data():
	generate_baseline_data()
	with open(commons.BASELINE_TEST_X, 'rb') as f:
		test_x = pickle.load(f)
	with open(commons.BASELINE_TEST_Y, 'rb') as f:
		test_y = pickle.load(f)
	with open(commons.BASELINE_TEST_WHO, 'r') as f:
		test_who = []
		for line in f.readlines():
			test_who.append(line.strip())
	return test_x, test_y, test_who

def shuffle_train(train_x, train_y):
	import random

	zipped = list(zip(train_x, train_y))
	random.shuffle(zipped)

	train_x = [item[0] for item in zipped]
	train_y = [item[1] for item in zipped]

	return train_x, train_y

def transform_x_y(x, y):
	x = [item.flatten() for item in x]
	y = [ 1 if item == 'BAD' else 0 for item in y ]
	return x, y

"""
Accept: 
X: flattened vgg16 last non-fully-connected layer
Y: GOOD = 0, BAD = 1
"""
def train_baseline():
	train_x, train_y = load_training_data()

	train_x = [item.flatten() for item in train_x]
	train_y = [ 1 if item == 'BAD' else 0 for item in train_y ]
	train_x, train_y = shuffle_train(train_x, train_y)

	svm = SVC(gamma='auto', class_weight='balanced')
	print("Training SVM...")
	svm.fit(train_x, train_y)

	from sklearn.externals import joblib
	joblib.dump(svm, commons.BASELINE_MODEL) 
	print("Model saved.")

def test_baseline():
	from sklearn.externals import joblib
	svm = joblib.load(commons.BASELINE_MODEL) 

	test_x, test_y, test_who = load_test_data()
	test_x, test_y = transform_x_y(test_x, test_y)

	result = svm.predict(test_x)
	assert(len(result) == len(test_y))

	# 1. naive accuracy
	correct = 0
	correct_by_type = [0, 0]
	count_by_type = [len([ y for y in test_y if y == 0 ]), len([ y for y in test_y if y == 1 ])]
	for i in range(len(result)):
		if result[i] == test_y[i]:
			correct += 1
			correct_by_type[result[i]] += 1

	print("naive accuracy: {}/{}".format(correct, len(result)))
	for i in range(len(correct_by_type)):
		print("naive accuracy type {}: {}/{}".format(i, correct_by_type[i], count_by_type[i]))

	# 2. majority voting accuracy
	resultof = defaultdict(lambda: defaultdict(list))
	label = commons.get_label()

	# 2.1 collect all the  votings
	for i in range(len(result)):
		imdb_id, character_id, _ = test_who[i].split('-')
		character_id = int(character_id)
		resultof[imdb_id][character_id].append(result[i])
		
	# 2.2 majority vote
	correct = 0
	correct_by_type = [0, 0]
	count_by_type = [0, 0]
	for imdb_id in resultof:
		for character_id in resultof[imdb_id]:
			true_label = (label[imdb_id][character_id] == "BAD")
			count = len([ x for x in resultof[imdb_id][character_id] if x == true_label ])
			if count >= len(resultof[imdb_id][character_id]) / 2:
				correct += 1
				correct_by_type[true_label] += 1

	# 2.3 how many characters
	count = 0 
	for imdb_id in resultof:
		count += len(resultof[imdb_id])

		for character_id in resultof[imdb_id]:
			true_label = (label[imdb_id][character_id] == "BAD")
			count_by_type[true_label] += 1

	print("accuracy by actor: {}/{}".format(correct, count))
	for i in range(len(correct_by_type)):
		print("accuracy by actor type {}: {}/{}".format(i, correct_by_type[i], count_by_type[i]))

if __name__ == '__main__':
	load_baseline_data()
	train_baseline()
	test_baseline()