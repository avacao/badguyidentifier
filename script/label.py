import ast
import os
import sys
import re
import webbrowser

# command 'python3 ./label.py {label_id} {IMDB_id_prefix}'
# label_id: required
# IMDB_id_prefix: optional
# sample 'python3 ./label.py 2 t01'
# Only movies starts with 't01' will be processed. 
# And your label will be stored in file _LABEL2.

FACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'faces')
LABEL_FILE = '_LABEL' + sys.argv[1]   # Label id is mandatory.
IMDB_ID_PREFIX = sys.argv[2] if len(sys.argv) > 2 else ''
SUCCESS_FILE = '_SUCCESS'
TIER_FILE = '_TIER'

OPTION_FORMAT = '\'{}\' or \'{}\' for \'{}\''

LEGAL_SELECTION = {'', '1', '2', '3', '4', 'G', 'B', 'N', 'NA'}
TIERS = {'EASY', 'MEDIUM', 'HARD'}

def get_movie_folders():
	return [name for name in os.listdir(FACE_DIR)
			if os.path.isdir(os.path.join(FACE_DIR, name)) and name.startswith(IMDB_ID_PREFIX) and 
				(not os.path.exists(os.path.join(FACE_DIR, name, LABEL_FILE)))]

def tag(movie):
	url, faces = parse_success(movie)

	print(('Working on movie', movie, "..."))
	eval(input('Press Enter to open video in browser...'))
	webbrowser.open(url)
	
	eval(input('Press Enter to start labelling...'))
	if not os.path.exists(os.path.join(FACE_DIR, movie, TIER_FILE)):
		write_to_tier(movie)

	labels = []
	for idx, pics in enumerate(faces):
		print(('Showing pics for character {} ...'.format(idx)))

		for idx, pic in enumerate(pics):
			show_pic(pic)
			label = ask_for_label()

			# Rare case: If there is no more pic for this character, user must label.
			while label == '' and idx == len(pics) - 1:
				print('\nERROR: no more pic for this character.\n')
				show_pic(pic)
				label = ask_for_label()

			# Label received, store it, and skip to the next character.
			if label != '':
				labels.append('{}:{}'.format(len(labels), label))
				break

	write_to_label(movie, labels)

def write_to_tier(movie):
	path = os.path.join(FACE_DIR, movie, TIER_FILE)
	tier = eval(input('Enter the tier for this movie:'))
	while tier not in TIERS:
		tier = eval(input('Reenter the tier for this movie, only EASY, MEDIUM, HARD are accepted:'))

	with open(os.path.abspath(path), "w") as f:
		f.write(tier)

	print((path, 'saved'))

def write_to_label(movie, labels):
	path = os.path.join(FACE_DIR, movie, LABEL_FILE)
	with open(os.path.abspath(path), "w") as f:
		f.write('\n'.join(labels))

	print((path, 'saved'))

def show_pic(pic):
	webbrowser.open('file://' + os.path.abspath(pic))

def ask_for_label():
	print((OPTION_FORMAT.format(1, 'G', 'GOOD')))
	print((OPTION_FORMAT.format(2, 'B', 'BAD')))
	print((OPTION_FORMAT.format(3, 'N', 'Neutral')))
	print((OPTION_FORMAT.format(4, 'NA', 'NOT APPLICABLE')))

	# Loop to handle selections. Typing legal input to break out.
	while True:
		selection = eval(input('Type your selection, or hit Enter to view next pic for this character:'))

		# Handle unknown input.
		if selection not in LEGAL_SELECTION:
			print('\nERROR: illegal input.\n')
			continue

		# Store label, and break out.
		if selection == '1' or selection == 'G':
			return 'GOOD'
		
		if selection == '2' or selection == 'B':
			return 'BAD'
		
		if selection == '3' or selection == 'N':
			return 'N'
		
		if selection == '4' or selection == 'NA':
			return 'NA'

		return ''

# parse '_SUCCESS', return the video url and the face files.
def parse_success(movie):
	with open(os.path.join(FACE_DIR, movie, SUCCESS_FILE)) as f:
		lines = f.readlines()
	
	# Parse youtube url.
	url = lines[-1][lines[-1].find('https://'):]

	# Parse face array.
	faceStrs = lines[:-1]
	faces = [parse_face(faceStr, movie) for faceStr in faceStrs]

	return url, faces

# Example parse_face("'0: [1, 2, 3]'") will return ['{path}/1.jpg', '{path}/2.jpg', '{path}/3.jpg']).
def parse_face(face, movie):
	# Get the picture array string and trim the leading space.
	pics = face.split(':')[1][1:]
	# Parse pics array.
	return [os.path.join(FACE_DIR, movie, str(pic) + '.jpg') for pic in ast.literal_eval(pics)]

def main():
	print('Label helper for badguyidentifier')
	print('\n***** CONFIG *****')
	print(('FACE_DIR =', FACE_DIR))
	print(('LABEL_FILE =', LABEL_FILE)) 
	print(('IMDB_ID_PREFIX =', IMDB_ID_PREFIX))
	print('******************\n')
	print('Start labelling...\n')
	movies = get_movie_folders()
	print(movies)

	print((len(movies), 'movies found'))
	for movie in movies:
		tag(movie)

if __name__ == "__main__":
	main()
