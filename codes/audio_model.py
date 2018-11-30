import sklearn, numpy
import commons, os, pickle
import baseline

from datetime import datetime

def load_training_data():
	with open(commons.AUDIO_BASELINE_TRAIN_X, 'rb') as f:
		train_x = pickle.load(f)
	with open(commons.AUDIO_BASELINE_TRAIN_Y, 'rb') as f:
		train_y = pickle.load(f)
	with open(commons.AUDIO_BASELINE_TRAIN_WHO, 'r') as f:
		train_who = []
		for line in f.readlines():
			train_who.append(line.strip())	
	return (train_x, train_y, train_who)

def load_test_data():
	with open(commons.AUDIO_BASELINE_TEST_X, 'rb') as f:
		test_x = pickle.load(f)
	with open(commons.AUDIO_BASELINE_TEST_Y, 'rb') as f:
		test_y = pickle.load(f)
	with open(commons.AUDIO_BASELINE_TEST_WHO, 'r') as f:
		test_who = []
		for line in f.readlines():
			test_who.append(line.strip())
	return (test_x, test_y, test_who)

if __name__ == '__main__':
	baseline.train(data=load_training_data(), model_path=commons.AUDIO_BASELINE_MODEL)
	baseline.test(data=load_test_data(), model_path=commons.AUDIO_BASELINE_MODEL)
