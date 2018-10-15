# badguyidentifier
CMU MCDS Capstone Project

### Start Point
Local: Activate python3 virtual environment by ```source venv/bin/activate```
Remote: 
1. Login to Bridges by ```ssh yuec1@bridges.psc.xsede.org``` and ```cd $SCRATCH```. 
2. Set up python: ```module load python3```.
3. Install dependencies: ```pip3 install -r dependencies.txt```

### Progress Log
Milestone 1 - COMPLETED - [2018/09/01 - 2018/09/09]

- Build a movie dataset of ~200 movies. They are fetched based on a set of rules from imdb each year's feature list.
- Download movie trailers and captions if available.


Milestone 2 - ONGOING - [2018/09/12 - ]
- Face recognition for each trailer. Cluster them into main characters with ~100% precision and ~90% recall