#!/bin/bash

# creating a virtual environment
python3 -m venv env_scraper

pip3 install pip --upgrade

# activating the virtual environment
source env_scraper/bin/activate

# installing the requirements
pip install -r requirements.txt --no-cache-dir

# running scraper
python3 database.py

# running scraper
python3 scraper.py