"""
Face identification and comparison in videos
"""

import commons
import face_recognition
import cv2, os

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

def save_faces(movies):
	for imdb_id in ["tt1843866", "tt3501632", "tt0264464"]:
	#for imdb_id in movies:
		movie = movies[imdb_id]

		input_movie = cv2.VideoCapture(commons.get_video_path(imdb_id))
		face_dir = commons.get_faces_dir(imdb_id)

		# check if this movie has already been face recognized
		if os.path.exists(face_dir) and os.path.exists(os.path.join(face_dir, '_SUCCESS')):
			print("movie {} has faces saved".format(movie.name))
			continue # skip this movie

		frame_count = input_movie.get(cv2.CAP_PROP_FRAME_COUNT)
		height = int(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
		width = int(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))

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


def face_clustering(movies):
	pass

if __name__ == '__main__':
	movies = commons.load_movies()
	save_faces(movies)