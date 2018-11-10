"""
Face identification and comparison in videos
"""

import commons
import face_recognition
import cv2, os, sys, shutil

FACE_FILTER_AREA_RATIO_LOWER_BOUND = 1.0 / 160
FACE_FILTER_AREA_GROUP_RATIO_LOWER_BOUND = 1.0 / 80
FACE_SCALE = 1.3

def visualization():
	input_movie = cv2.VideoCapture(commons.get_video_path("tt3501632"))
	frames_count = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

	height = int(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
	width = int(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))

	output_movie = cv2.VideoWriter('tt3501632_output.avi', -1, 29.97, (width, height))

	frame_number = 0
	while True:
		ret, frame = input_movie.read()
		frame_number += 1

		if not ret:
			break

		rgb_frame = frame[:, :, ::-1] # conver bgr color to rgb color
		face_locations = face_recognition.face_locations(rgb_frame)
		face_locations = filter_face(face_locations, height * width)

		for top, right, bottom, left in face_locations:
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
		print("Writing frame {} / {}".format(frame_number, frames_count), end="\r")
		output_movie.write(frame)

	print()

	input_movie.release()
	output_movie.release()
	cv2.destroyAllWindows()

"""
Given all face locations in a particular frame,
filter out some faces by rule of thumb: 
 - face area too small  
"""
def filter_face(face_locations, screen_area):
	ret = []
	screen_area = float(screen_area)

	for top, right, bottom, left in face_locations:
		face_area = abs((top - bottom) * (right - left))

		if face_area / screen_area < FACE_FILTER_AREA_RATIO_LOWER_BOUND:
			continue
		if len(face_locations) > 3 and \
			face_area / screen_area < FACE_FILTER_AREA_GROUP_RATIO_LOWER_BOUND:
			continue

		ret.append((top, right, bottom, left))

	return ret

def scale_face_rectangle(top, right, bottom, left, height, width):
	top = max(0, int((top+bottom)/2 - abs(bottom-top)/2 * FACE_SCALE))
	bottom = min(height, int((top+bottom)/2 + abs(bottom-top)/2 * FACE_SCALE))
	right = min(width, int((right+left)/2 + abs(right-left)/2 * FACE_SCALE))
	left = max(0, int((right+left)/2 - abs(right-left)/2 * FACE_SCALE))
	return top, right, bottom, left

"""
Used for generate groundtruth label. Extract faces appeared for each trailer.
"""
def save_faces(movies):
	errors = []

	for imdb_id in movies:
		movie = movies[imdb_id]

		input_movie = cv2.VideoCapture(commons.get_video_path(imdb_id))
		face_dir = commons.get_faces_dir(imdb_id)

		# check if this movie has already been face recognized
		if os.path.exists(face_dir) and os.path.exists(os.path.join(face_dir, '_SUCCESS')):
			print("movie {} has faces saved".format(movie.name))
			continue # skip this movie
		print("movie {}: ".format(movie.name))

		frame_count = input_movie.get(cv2.CAP_PROP_FRAME_COUNT)
		height = int(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
		width = int(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))


		if frame_count == 0.0:
			error_msg = "ERROR: movie <{}> {} does not have a trailer.\n"\
				.format(imdb_id, movie.name)
			errors.append(error_msg)

			input_movie.release()
			cv2.destroyAllWindows()
			continue


		i, face_count = -1, 0
		while True:
			ret, bgr_frame = input_movie.read()
			i += 1

			if not ret:
				break

			# only sample 1 out of every 4 frames
			if i % 4 != 0:
				continue

			# face recognition
			rgb_frame = bgr_frame[:,:,::-1]
			face_locations = face_recognition.face_locations(rgb_frame)
			face_locations = filter_face(face_locations, height * width)

			# save faces
			for j in range(len(face_locations)):
				top, right, bottom, left = scale_face_rectangle(
					*face_locations[j], height, width)

				face = rgb_frame[top:bottom, left:right]
				face = face[:,:,::-1]

				cv2.imwrite(face_dir + "{}.jpg".format(face_count), face)
				face_count += 1

			print("At frame {} / {} ...".format(i, frame_count),end="\r")

		print(" Done.")
		open(os.path.join(face_dir, '_SUCCESS'), "a").close() # mark success
		input_movie.release()
		cv2.destroyAllWindows()

	for error_msg in errors:
		print(error_msg)

"""
Given a list of T/F results (current face against a list of known faces),
determine whether they belong to the same person
"""
def is_same_person(result):
	true_count = len(list(filter(lambda x: x, result)))
	return true_count >= (len(result) / 2.0)

"""
Generate groundtruth label.
Using extracted faces in folder, identify main characters and re-ID
"""
def face_clustering(movies):
	errors = []

	for imdb_id in movies:
		movie = movies[imdb_id]
		face_dir = commons.get_faces_dir(imdb_id)

		# check if face detection has succeeded
		if not os.path.exists(os.path.join(face_dir, '_SUCCESS')):
			error_msg = "ERROR: movie <{}> {} face not extracted.".format(imdb_id, movie.name)
			errors.append(error_msg)
			continue

		# open all faces
		# NOTE: maybe keep file sequence to use heuistics?
		faces = {} # integer of filename -> face image
		for file in os.listdir(face_dir):
			filename, extension = os.path.splitext(file)
			if extension == ".jpg":
				faces[int(filename)] = face_recognition.load_image_file(os.path.join(face_dir, file))


		# re-ID
		"""
		Given a list of T/F results (current face against a list of known faces),
		determine whether they belong to the same person
		"""
		def is_same_person(result):
			true_count = len(list(filter(lambda x: x, result)))
			return true_count >= (len(result) / 2.0)

		clusters = [] # lists of (index, encoding)

		for index in sorted(faces.keys()):
			face = faces[index]
			try:
				encoding = face_recognition.face_encodings(face)[0]
			except IndexError: # face not found (aha)
				continue

			found = False
			for i in range(len(clusters)):
				cluster = clusters[i]
				result = face_recognition.compare_faces([x[1] for x in cluster], encoding)

				if is_same_person(result):
					cluster.append((index, encoding))
					found = True
					break

			if not found:
				clusters.append([(index, encoding)])

		# post-process to increase accuracy: starting from clusters with least # faces,
		# check with previous clusters to see if they belong to the same person.
		# if true, merge, else discard cluster. We value precision higher than recall.
		for i in range(len(clusters) - 1, -1, -1):
			cluster = clusters[i]

			# check face one by one (since precision is the most important)
			for k in range(len(cluster) -1, -1, -1):
				index, encoding = cluster[k]

				for other_cluster in clusters[:i]:
					result = face_recognition.compare_faces([x[1] for x in other_cluster], encoding)

					# if same, delete k-th element from current cluster, add it to main cluster
					if is_same_person(result):
						other_cluster.append((index, encoding))
						cluster.pop(k)
						break
					# otherwise do nothing

			# delete this cluster if it is not main_character
			if len(cluster) < 10:
				clusters.pop(i)

		# save all results to _SUCCESS
		with open(os.path.join(face_dir, '_SUCCESS'), 'w') as f:
			for i in range(len(clusters)):
				indices = [x[0] for x in clusters[i]]
				f.write("{}: {}\n".format(i, indices))

			f.write("#youtube url: https://www.youtube.com/watch?v={}\n".format(movie.video_id))
		    
			print("Movie <{}> {} face clustering done.".format(imdb_id, movie.name))


############ IMAGE PREPROCESSING ############

SAMPLE_FRAME_RATE = 6

def format_image_filename(imdb_id, char_index, timestamp):
	return "{}-{}-{}.jpg".format(imdb_id, char_index, timestamp)

def get_temp_images_dir(imdb_id):
	return commons.IMAGE_DIR + imdb_id + '/'

"""
If this movie has completed images preprocess.
If yes, return True, otherwise, cleanup previous record and start fresh
"""
def images_completed(imdb_id):
	# already succeeded
	if os.path.exists(commons.IMAGE_DONE_DIR + imdb_id):
		return True

	# parially done
	if os.path.exists(get_temp_images_dir(imdb_id)):
		shutil.rmtree(get_temp_images_dir(imdb_id))

	# make new temp directory
	os.mkdir(get_temp_images_dir(imdb_id))

	return False

def save_images(movies):
	errors = []
	commons.create_images_dir_if_not_exists()

	for imdb_id in movies:
		movie = movies[imdb_id]
		print("save images for <{}> {}...".format(imdb_id, movie.name))

		if images_completed(imdb_id):
			print("Already done.".format(imdb_id, movie.name))
			continue

		try:
			input_movie = cv2.VideoCapture(commons.get_video_path(imdb_id))
			characters = commons.get_characters(imdb_id)
			temp_image_dir = get_temp_images_dir(imdb_id)

		except Exception as e:
			errors.append(e)
			continue

		frame_count = input_movie.get(cv2.CAP_PROP_FRAME_COUNT)
		height = int(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
		width = int(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))

		if frame_count == 0.0:
			error_msg = "ERROR: movie <{}> {} does not have a trailer.\n"\
				.format(imdb_id, movie.name)
			errors.append(error_msg)

			input_movie.release()
			cv2.destroyAllWindows()
			continue

		frame_i = -1
		while True:
			ret, bgr_frame = input_movie.read()
			frame_i += 1

			if not ret:
				break

			# only sample 1 out of every 4 frames
			if frame_i % SAMPLE_FRAME_RATE != 0:
				continue

			print("At frame {} / {} ...".format(frame_i, frame_count), end="\r")

			# face recognition
			rgb_frame = bgr_frame[:,:,::-1]
			encodings = face_recognition.face_encodings(rgb_frame)

			# compare each face encoding with main characters encodings
			for encoding in encodings:
				char_index = -1
				for i in range(len(characters)):
					result = face_recognition.compare_faces(characters[i], encoding)
					if is_same_person(result):
						char_index = i 
						break

				if char_index > -1:
					# valid image! save image with desired format
					image_filename = temp_image_dir + \
						format_image_filename(imdb_id, char_index, input_movie.get(cv2.CAP_PROP_POS_MSEC))
					cv2.imwrite(image_filename, bgr_frame)

		print(" Done.")

		# move all images out of temp_image_dir to IMAGE_DIR, delete temp dir, mark success
		for file in os.listdir(temp_image_dir):
			filename, extension = os.path.splitext(file)
			if extension == ".jpg":
				shutil.move(os.path.join(temp_image_dir, file), os.path.join(commons.IMAGE_DIR, file))
		shutil.rmtree(temp_image_dir)
		open(os.path.join(commons.IMAGE_DONE_DIR, imdb_id), "a").close()

		# cleanup
		input_movie.release()
		cv2.destroyAllWindows()

	for error_msg in errors:
		print(error_msg)

if __name__ == '__main__':
	movies = commons.load_movies()
	#save_faces(movies)
	#face_clustering(movies)

	save_images(movies)
