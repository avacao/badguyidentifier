## DATA FOLDER
This folder stores the valueable dataset we generate!

#### keyvalue.pkl
The key-value python3 dictionary file that stores info for each movie in dataset.
Dictionary is defined as imdb_id (primary key) -> a movie object.

#### videos
A folder contains all movie trailers. Named by [imdb_id].mp4

#### captions
A folder contains movie trailer caption. Named by [imdb_id].txt

#### faces
A folder of folders. Each subfolder is of the name [imdb_id], containing a list of faces <index>.jpg cropped from trailer. 
If a `_SUCCESS` file exists, it means the face extraction is completed.
	
`_LABEL<k>`: k stands for the person labeling that movie.

- Bad: unlawful actions, lack of sympathy to others
- Good: (lawful actions AND normal person we run into everyday), OR positive human traits 
- N(eutral): mixed bad guy traits and good guy trait, or appears to be a main character but lack any obvious traits
- NA: not a main character
