import commons
import face_recognition
import cv2, os, sys, pickle

"""
Genarate a list where index i -> [ face_recognition encodings of character i ]
save in face dir
"""
def generate_character_encodings():

	"""
	Returns a list, where index i = [ face_recognition images ] of character i
	"""
	def get_characters(imdb_id):
		import ast

		face_dir = commons.get_faces_dir(imdb_id)

		# check if directory exists and face cluster is done
		if not (os.path.exists(face_dir) and os.path.exists(os.path.join(face_dir, '_SUCCESS'))):
			raise RuntimeError("movie <{}> {} face_dir / _SUCCESS not exists.".format(imdb_id, movies[imdb_id].name))

		character_indices = [] 

		with open(os.path.join(face_dir, '_SUCCESS'), 'r') as f:
			for line in f.readlines():
				if len(line) > 0 and line[0] != '#':
					character_indices.append( ast.literal_eval( line.split(':')[1].strip() ))

		faces = commons.open_faces_of_movie(imdb_id)

		characters = []
		for i in range(len(character_indices)):
			encodings = []
			for number in character_indices[i]:
				try:
					encodings.append( face_recognition.face_encodings(faces[number])[0] )
				except IndexError: # face not found
					continue
			characters.append(encodings)

		return characters


	movies = commons.load_movies()
	for imdb_id in movies:

		if os.path.exists(commons.get_characters_path(imdb_id)):
			continue

		characters = get_characters(imdb_id)
		with open(commons.get_characters_path(imdb_id), 'wb') as f:
			pickle.dump(characters, f)

if __name__ == '__main__':
	generate_character_encodings()