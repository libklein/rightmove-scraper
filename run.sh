#!/bin/sh

# Create the database
python rightmove_scraper/models.py

scrapy crawl rightmove
