import commons, face
import face_recognition, cv2, numpy
from scipy.io import wavfile # for breaking audio files
import os, sys, pickle, multiprocessing, shutil, subprocess
from collections import defaultdict

#################### IMAGE PREPARATION ####################

"""
INPUT: cv2 image
OUTPUT: cv image removed black edge in y direction
"""
def remove_black_edge(image, thres=0):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	
	y0 = 0
	while max(gray[y0]) == thres:
		y0 += 1

	y1 = gray.shape[0] - 1
	while max(gray[y1]) == thres:
		y1 -= 1	

	crop = image[y0:y1]
	return crop

"""
prepare images for training
INPUT: IMAGE_DIR
OUTPUT: TRAIN_IMAGES_DIR
"""
def prepare_images():
	# 0. safety check
	if not os.path.exists(commons.IMAGE_DIR):
		print("ERROR: IMAGE_DIR {} not exist.".format(commons.IMAGE_DIR))

	if not os.path.exists(commons.TRAIN_IMAGES_DIR):
		os.mkdir(commons.TRAIN_IMAGES_DIR)

	if not os.path.exists(commons.TRAIN_IMAGES_DONE_DIR):
		os.mkdir(commons.TRAIN_IMAGES_DONE_DIR)

	movies = commons.load_movies()
	images =  [ x for x in sorted(os.listdir(commons.IMAGE_DIR)) if len(x) > 4 and x[-4:] == ".jpg" ]
	errors = []

	# 1. categorize images into imdb_id -> character_id -> list of images belonging to that id
	print("Categorizing images...")
	imagesof = defaultdict(lambda: defaultdict(list))
	for x in images:
		# already prepared
		if os.path.exists(os.path.join(commons.TRAIN_IMAGES_DIR, x)):
			continue

		imdb_id, character_id, timestamp = x[:-4].split('-')
		character_id = int(character_id)
		imagesof[imdb_id][character_id].append(x)

	# 2. locate face for each image with black edge cropped
	for imdb_id in imagesof:
		print("Prepare images for <{}> {}...".format(imdb_id, movies[imdb_id].name))
		if os.path.exists(os.path.join(commons.TRAIN_IMAGES_DONE_DIR, imdb_id)):
			continue

		character_encodings = commons.get_characters(imdb_id)

		for character_id in imagesof[imdb_id]:
			for x in imagesof[imdb_id][character_id]:
				try:
					image = cv2.imread(os.path.join(commons.IMAGE_DIR, x))
					image = remove_black_edge(image)

					rgb_image = image[:,:,::-1]
					face_locations = face_recognition.face_locations(rgb_image)
					encodings = face_recognition.face_encodings(rgb_image, known_face_locations=face_locations)
				except Exception:
					print("ERROR {}".format(e))
					errors.append(e)

				for i in range(len(face_locations)):
					try:
						result = face_recognition.compare_faces(character_encodings[character_id], encodings[i])
						if face.is_same_person(result):
							height, _ , _ = image.shape
							_, right, _, left = face_locations[i]
							mid = int((left + right) / 2)

							height = height if height % 2 == 0 else height - 1

							x0 = max(0, mid - int(height / 2))
							x1 = x0 + height

							rect_image = image[0: height, x0:x1]
							cv2.imwrite(os.path.join(commons.TRAIN_IMAGES_DIR, x), rect_image)

					except Exception as e:
						print("ERROR {}".format(e))
						errors.append(e)

		open(os.path.join(commons.TRAIN_IMAGES_DONE_DIR, imdb_id), "a").close()

	for e in errors:
		print(e)

#################### TRAIN & TEST ####################

def generate_train_and_test():
	import random 

	movies = commons.load_movies()
	TEST_PERCENT = 0.2

	test = random.sample(movies.keys(), int(TEST_PERCENT * len(movies)))
	train = list(set(movies.keys()) - set(test))
	
	assert len(set(test).intersection(train)) == 0

	with open(commons.TRAIN_FILE, 'w') as f:
		for imdb_id in train:
			f.write("{}\n".format(imdb_id))

	with open(commons.TEST_FILE, 'w') as f:
		for imdb_id in test:
			f.write("{}\n".format(imdb_id))
	
#################### AUDIO PREPROCESSING ####################

def extract_audio_from_video_worker(imdb_id):
	video_path = os.path.join(commons.VIDEO_DIR, "{}.mp4".format(imdb_id))
	audio_path = os.path.join(commons.AUDIO_DIR, "{}.wav".format(imdb_id))
	cmd = "ffmpeg -hide_banner -loglevel panic -i {} {}".format(video_path, audio_path)

	if os.path.exists(video_path):
		try:
			subprocess.run(cmd, shell=True)
			print("<{}> completed.".format(imdb_id))
		except Exception as e:
			print("ERROR <{}>: {}".format(imdb_id, e))


def extract_audio_from_video():
	movies = commons.load_movies()
	print("Extract audio from video.")
	print("Number of cores: {}".format(multiprocessing.cpu_count()))

	if not os.path.exists(commons.AUDIO_DIR):
		os.mkdir(commons.AUDIO_DIR)

	pool = multiprocessing.Pool(multiprocessing.cpu_count())
	pool.map(extract_audio_from_video_worker, movies.keys())

"""
Find continuous frames in video that corresponds to one specific character.
"""
def is_the_same_scene(scene, timestamp):
	if len(scene) > 0 and abs(scene[-1] - timestamp) > 500:
		return False
	return True

def filter_scene(scenes):
	return [ s for s in scenes if len(s) >= 5 ]

def generate_audio_features():
	movies = commons.load_movies()
	print("Extract audio pieces...")

	# if not os.path.exists(commons.AUDIO_UNIT_DIR):
	# 	os.mkdir(commons.AUDIO_UNIT_DIR)
	# if not os.path.exists(commons.AUDIO_UNIT_DONE_DIR):
	# 	os.mkdir(commons.AUDIO_UNIT_DONE_DIR)

	labelof = commons.get_label()
	train_ids, test_ids = commons.get_train_and_test_imbd_ids()
	train_x, train_y, test_x, test_y, test_who = [], [], [], [], []

	if not os.path.exists(commons.AUDIO_BASELINE_DIR):
		os.mkdir(commons.AUDIO_BASELINE_DIR)

	#for imdb_id in movies:
	for imdb_id in ['tt0264464', 'tt1843866', 'tt3501632']:
		temp_audio_unit_path = os.path.join(commons.AUDIO_UNIT_DIR, imdb_id)

		# 0. clean up work if exists
		if os.path.exists(os.path.join(commons.AUDIO_UNIT_DONE_DIR, imdb_id)):
			print("<{}> already completed.".format(imdb_id))
			return
		if os.path.exists(os.path.join(commons.AUDIO_UNIT_DIR, imdb_id)):
			shutil.rmtree(temp_audio_unit_path)

		# 1. create temp path and start working!
		os.mkdir(temp_audio_unit_path)
		frames = [ x for x in os.listdir(commons.TRAIN_IMAGES_DIR) if x.startswith(imdb_id) ]

		timestampsof = defaultdict(list) # character_id -> timestamps
		for frame in frames:
			_, character_id, timestamp = frame[:-4].split('-')
			character_id = int(character_id)
			timestamp = float(timestamp)
			timestampsof[character_id].append(timestamp)
		for character_id in timestampsof:
			timestampsof[character_id].sort()

		scenes = defaultdict(list) # character_id -> [ scene0 = [ timestamp0 ... ] ]
								   # timestamp is a float exactly what in train_image, in milisecond
		curr_scene = []
		for character_id in timestampsof:
			for timestamp in timestampsof[character_id]:
				if not is_the_same_scene(curr_scene, timestamp):
					scenes[character_id].append(curr_scene)
					curr_scene = []
				curr_scene.append(timestamp)

			scenes[character_id].append(curr_scene)
			curr_scene = []

		for character_id in scenes:
			scenes[character_id] = filter_scene(scenes[character_id])

		# 2. from character_id -> a list of scene [timestamps], 
		# 	 extract audio file and save to train/test 
		# 	 NOTE: we need to write because we don't know how to convert scipy wavfile to
		# 		   format known to pyAudioAnalysis
		partial_xs = []
		rate, data = wavfile.read(os.path.join(commons.AUDIO_DIR, "{}.wav".format(imdb_id)))
		for c_id in scenes:
			for scene in scenes[c_id]:
				# clip audio of this scene
				start, end = scene[0], scene[-1]
				start_sec, end_sec = start / 1000, end / 1000 # convert to seconds
				start_frame, end_frame = int(start_sec * rate), int(end_sec * rate)
				x = data[start_frame: end_frame + 1]

				# get audio features of this scene
				from pyAudioAnalysis import audioFeatureExtraction

				x = x.sum(axis=1) / 2 # stereo to mono
				features, _ = audioFeatureExtraction.stFeatureExtraction(x, rate, 
																		0.05*rate, #frame size
												   0.025*(end_frame+1-start_frame)) #frame step
				features = features[:, :39] # drop extra frame data ... sign
				features.flatten()
				
				# add (x, y) 
				label = labelof[imdb_id][c_id]
				if imdb_id in train_ids:
					train_x.append(features)
					train_y.append(label)
				else:
					test_x.append(features)
					test_y.append(label)
					test_who.append("{}-{}-{}~{}".format(imdb_id, c_id, start, end))				

		print("<{}> Finished".format(imdb_id))

	with open(commons.AUDIO_BASELINE_TRAIN_X, 'wb') as f:
		pickle.dump(train_x, f)
	with open(commons.AUDIO_BASELINE_TRAIN_Y, 'wb') as f:
		pickle.dump(train_y, f)
	with open(commons.AUDIO_BASELINE_TEST_X, 'wb') as f:
		pickle.dump(test_x, f)
	with open(commons.AUDIO_BASELINE_TEST_Y, 'wb') as f:
		pickle.dump(test_y, f)
	with open(commons.AUDIO_BASELINE_TEST_WHO, 'w') as f:
		for who in test_who:
			f.write(who + '\n')

if __name__ == "__main__":
	#generate_train_and_test()
	#prepare_images()
	#extract_audio_from_video()
	generate_audio_features()