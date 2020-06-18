# Description
This is a coindesk.com articles scraper. It uses Selenium.Firefox.
The scraper saves metadata and text of articles in sqlite3 database.
As we do not want the overload the coindesk servers this scraper takes its time to scrape the articles. This repository does not include database. When you will start the scraper for the first time it will create new empty database.

# Dependencies
Sadly I was not able to create requirements.txt, but required libraries
that are not in Python's standard library packages. Will do automated instalation later on.

- lxml
- dateutil
- selenium

The Python version that I have tested is 3.5 and later.
The scraper will work on Linux machines. I have tested it on Ubuntu 16.04 and later. If you plan to use it for some mysterious reason on MS Windows or on Apple OS machine you are on your own.

# GUI
No GUI at this time. The scraper prints what was downloaded into console. If there is a interest I can make desktop GUI. Let me know.

# Documentation
There is some documentation in the files, but definitely not enough. Sorry. Very likely I will add it further down the road.

# Starting
1. git clone to appropriate directory
2. install abovementioned libraries
3. python3 coindesk.py

# Parameters
You can add number of how many articles are to be scraped for each category. By default 50 articles are scraped. Scraper count into this number articles that are already saved in the database.

To specify parameter use for example:
python3 coindesk.py 500

Word of warning here. Scraper does not use async or other paralellization protocols if  you are planning to use high number it will take its sweet time. Let me know if you are interested in paralellization.


# How it works
Firstly, headless Firefox is initiated.

There is a list of categories that the scraper will go through.

Based on the number of articles that needs to be scraped (50 by default) scraper will go through article by article in each category and saves individual article's metadata - title, tags, publication/update dates, link, etc and articles text.  Check the database table for columns if you are interested.

Scraper then saves these articles to the database.

Thats it.

# Use
I am using scraped articles for NLP tasks including setting up specialized crypto corpora. The articles text should be easy to tokenize including paragraphs.

Plese let me know if you find other uses for it.
