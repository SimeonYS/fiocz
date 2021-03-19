import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FioczItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FioczSpider(scrapy.Spider):
	name = 'fiocz'
	offset = 0
	start_urls = [f'https://www.fio.cz/company-fio/media/breaking-news?offset={offset}']

	def parse(self, response):
		post_links = response.xpath('//h6/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = 'https://www.fio.cz/company-fio/media/breaking-news?offset={}'
		if len(post_links) == 12:
			self.offset += 12
			yield response.follow(next_page.format(self.offset), self.parse)

	def parse_post(self, response):

		date = response.xpath('//p[@class="meta"]/text()').get().strip().split(' ')[0]
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="section3 newsSection"]//text()[not (ancestor::p[@class="meta"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FioczItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
