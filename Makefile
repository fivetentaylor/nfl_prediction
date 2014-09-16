all : boxscores.csv db.csv

parse : boxscores.csv parse_html.py
	./parse_html.py

scrape : 
	scrapy crawl boxscores -o boxscores.csv -t csv

