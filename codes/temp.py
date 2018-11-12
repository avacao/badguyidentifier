import commons
import os


def count_labels():
	movies = commons.load_movies()
	count = 0
	for imdb_id in movies:
		face_dir = commons.get_faces_dir(imdb_id)

		labels = ["_LABEL{}".format(i) for i in range(1, 4)]
		for label in labels:
			if os.path.exists(os.path.join(face_dir, label)):
				count += 1
				break

		if os.path.exists(os.path.join(face_dir, "_LABEL")):
			print("need to fix {}".format(imdb_id))

	print("Labeled movies: {}/{}".format(count, len(movies)))

if __name__ == "__main__":
	count_labels()