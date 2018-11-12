import commons
import sklearn, pickle, random
from collections import defaultdict, Counter

LABEL_TO_DIGIT = { 'GOOD': 0, 'BAD': 1, 'N': 2, 'NA': 3 }
DIGITS = sorted(list(set(LABEL_TO_DIGIT.values())))

"""
What is the f1_score for random guessing?
"""
def get_lowerbound_f1_score(test_y_file_path):
	labelof = commons.get_label()

	with open(test_y_file_path, 'rb') as f:
		test_y = pickle.load(f)
	test_y = [ LABEL_TO_DIGIT[item] for item in test_y ]

	random_y = [ random.randint(min(DIGITS), max(DIGITS)) for i in range(len(test_y)) ]
	all_good_y = [ LABEL_TO_DIGIT['GOOD'] for i in range(len(test_y)) ]

	count = Counter(test_y)
	count = [ count[i] for i in DIGITS ]
	weighted_random_y = random.choices(DIGITS, weights=count, k=len(test_y))

	print("random y: {}".format(random_y))
	print("all good y: {}".format(all_good_y))
	print("weighted random y: {}".format(weighted_random_y))

	random_score = sklearn.metrics.f1_score(test_y, random_y, average='weighted')
	all_good_score = sklearn.metrics.f1_score(test_y, all_good_y, average='weighted')
	weighted_random_score = sklearn.metrics.f1_score(test_y, weighted_random_y, average='weighted')

	print("random score: {}".format(random_score))
	print("all good score: {}".format(all_good_score))
	print("weighted random score: {}".format(weighted_random_score))

if __name__ == '__main__':
	import vggface
	get_lowerbound_f1_score(vggface.VGGFACE_DIR + '/' + vggface.TEST_Y)