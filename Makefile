db.csv : boxscores.csv parse_html.py
	./parse_html.py

boxscores.csv : 
	scrapy crawl boxscores -o boxscores.csv -t csv

