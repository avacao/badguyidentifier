import commons, face
import face_recognition
import cv2, os, sys, pickle, multiprocessing, subprocess
from collections import defaultdict

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


if __name__ == "__main__":
	#generate_train_and_test()
	#prepare_images()
	extract_audio_from_video()