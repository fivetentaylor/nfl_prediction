# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Boxscore(Item):
	linescore = Field()
	game_info = Field()
	scoring = Field()
	team_stats = Field()
	skill_stats = Field()
	def_stats = Field()
	kick_stats = Field()
	title = Field()
	url = Field()

