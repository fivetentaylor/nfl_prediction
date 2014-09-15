#from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from nfl_data.items import Boxscore
#from scrapy.contrib.loader import XPathItemLoader
import re

class BoxscoresSpider(CrawlSpider):
    name = 'boxscores'
    allowed_domains = ['pro-football-reference.com']
    start_urls = ['http://www.pro-football-reference.com']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'/boxscores/$', restrict_xpaths='//*[@id="quick_index"]/ul')),
        Rule(SgmlLinkExtractor(allow=r'/years/[0-9]{4}/games\.htm', restrict_xpaths='//*[@id="page_content"]/table[1]/tr/td[a > 2003]/a')),
        Rule(SgmlLinkExtractor(allow=r'/boxscores/.*\.htm', restrict_xpaths='//*[@id="div_games"]'), callback='parse_item')
    )

    def parse_item(self, response):
		# self.log('Hi, this is an item page! %s' % response.url)
		#hxs = HtmlXPathSelector(response)
		hxs = Selector(response)
		item = Boxscore()
		
		week = hxs.xpath('//*/table/tr/td[contains(.,"Week")]/text()')
		if len(week):
			item['week'] = week[0].extract()
			item['linescore'] = re.sub('\n', '', hxs.xpath('//*[@id="linescore"]').extract()[0])
			item['game_info'] = re.sub('\n', '', hxs.xpath('//*[@id="game_info"]').extract()[0])
			item['scoring'] = re.sub('\n', '', hxs.xpath('//*[@id="scoring"]').extract()[0])
			item['team_stats'] = re.sub('\n', '', hxs.xpath('//*[@id="team_stats"]').extract()[0])
			item['skill_stats'] = re.sub('\n', '', hxs.xpath('//*[@id="skill_stats"]').extract()[0])
			item['def_stats'] = re.sub('\n', '', hxs.xpath('//*[@id="def_stats"]').extract()[0])
			item['kick_stats'] = re.sub('\n', '', hxs.xpath('//*[@id="kick_stats"]').extract()[0])
			item['title'] = hxs.xpath('/html/head/title/text()').extract()[0]
			item['url'] =  response.url
			return item
		else:
			return None



