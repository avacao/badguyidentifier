import commons
import os, numpy
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

def count_labels():
	movies = commons.load_movies()
	count = 0
	for imdb_id in movies:
		face_dir = commons.get_faces_dir(imdb_id)

		labels = ["_LABEL{}".format(i) for i in range(1, 2)]
		for label in labels:
			if os.path.exists(os.path.join(face_dir, label)):
				count += 1
				break

		if os.path.exists(os.path.join(face_dir, "_LABEL")):
			print("need to fix {}".format(imdb_id))

	print("Labeled movies: {}/{}".format(count, len(movies)))

def count_overlap_labels():
	movies = commons.load_movies()
	count = 0
	for imdb_id in movies:
		face_dir = commons.get_faces_dir(imdb_id)

		labels = ['_LABEL1', '_LABEL2']
		exist = [os.path.exists(os.path.join(face_dir, label)) for label in labels]

		if sum(exist) > 1:
			count += 1

	print("2 Labeled movies: {}/{}".format(count, len(movies)))	

def labeler_disagreement():
	import baseline 

	movies = commons.load_movies()
	labelof = [ [], [] ]
	label_files = ['_LABEL1', '_LABEL2']
	label_to_digit = {'GOOD':0, 'BAD':0, 'NA':0, 'N':1}

	for imdb_id in movies:
		face_dir = commons.get_faces_dir(imdb_id)

		# only look at movies with more than one label
		if sum([ os.path.exists(os.path.join(face_dir, label_file)) for label_file in label_files ]) > 1:
			for i in range(len(label_files)):
				with open(os.path.join(face_dir, label_files[i]), 'r') as f:
					lines = f.readlines()
					for line in lines:
						if len(line) > 2:
							_, label = line.strip().split(':')

							# corner case
							if len(label) > 6 and label[:6] == "SAMEAS":
								label = lines[int(label[6:])].strip().split(':')[1]
							labelof[i].append(label_to_digit[label])

	assert(len(labelof[0]) == len(labelof[1]))

	baseline.f1_score(labelof[1], labelof[0])
	print("number of characters ", len(labelof[1]))


def character_statistics():
	labelof = commons.get_label()

	count = []
	labels = ['GOOD','BAD','N','NA']
	label_count = defaultdict(list)

	for imdb_id in labelof:
		count.append(len(labelof[imdb_id]))
		counter = Counter(labelof[imdb_id].values())
		for label in labels:
			label_count[label].append(counter[label])

	mean = numpy.mean(count)
	std = numpy.std(count)
	summ = sum(count)
	print("mean = {} , std = {} , sum = {}".format(mean, std, summ))

	label_mean, label_std = [], []
	for label in labels:
		label_mean.append(numpy.mean(label_count[label]))
		label_std.append(numpy.std(label_count[label]))

	# plot label distribution
	fig, ax = plt.subplots()
	indent, width = numpy.arange(len(labels)), 0.5
	rect = ax.bar(indent, label_mean, width, color='w', yerr=label_std, edgecolor='black', 
			error_kw={'linestyle':':', 'markersize':2,'capsize':4})
	ax.set_title('Distribution of classes per movie')
	ax.set_xticks(indent)
	ax.set_xticklabels(labels)

	for r in rect:
		height = r.get_height()
		ax.text(r.get_x() + r.get_width()/2., 1.05*height,
			"{0:.2f}".format(height),
			ha='center', va='bottom')

	plt.show()

def plot_audio_frequencies():
	candidate = "tt3501632.wav"
	time_start = 51593.20833333333
	time_end = 52594.20833333333

	from scipy.io import wavfile
	import matplotlib.pyplot as plt

	file = os.path.join(commons.AUDIO_DIR, candidate)
	rate, data = wavfile.read(file)
	start_frame, end_frame = int(time_start/1000 * rate), int(time_end/1000 * rate)
	data = data[start_frame: end_frame+1]

	plt.figure(figsize=(10,1))
	plt.plot(data)
	plt.show()

def get_model_mean_and_std():
	result = [0.2960529780896421,0.25016700124052765,0.2613629825404122,0.16530473681941815,0.19813488764600606,0.26405254307523485,0.3343727125275511,
		0.16284821971333036,0.18722157477086154,0.29563080661176533]
	print(numpy.mean(result), numpy.std(result))

if __name__ == "__main__":
	#count_labels()
	#character_statistics()
	#count_overlap_labels()
	#labeler_disagreement()
	#plot_audio_frequencies()
	get_model_mean_and_std()