# badguyidentifier
CMU MCDS Capstone Project

### Start Point
Local: Activate python3 virtual environment by ```source venv/bin/activate```

Remote: 
1. Choose an EC2 instance >= t2.large, with ubuntu as OS
2. sudo apt install git python3 python3-pip python python2-pip awscli
3. start venv. pip3 install cmake. pip3 install -r dependencies


### Saving Work
Remote:
1. Need to backup data to s3: `aws s3 sync badguyidentifier s3://yue-cao-capstone`

### Progress Log
Milestone 1 - COMPLETED - [2018/09/01 - 2018/09/09]

- Build a movie dataset of ~200 movies. They are fetched based on a set of rules from imdb each year's feature list.
- Download movie trailers and captions if available.


Milestone 2 - ONGOING - [2018/09/12 - ] 
- Face recognition for each trailer, and clustered them into main characters.
	- Main characters identification: 100% recall. Within each chracter, internal face precision ~100%, recall ~90%.
- Manually label each trailer's main character as GOOD / BAD / N (unknown/neutral)