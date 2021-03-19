import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FioczItem
from itemloaders.processors import TakeFirst
from scrapy.exceptions import CloseSpider
pattern = r'(\xa0)?'


class PressSpider(scrapy.Spider):
    name = 'press'
    offset = 0
    start_urls = [f'https://www.fio.cz/about-us/media/press-releases?offset={offset}']
    ITEM_PIPELINES = {
        'press.pipelines.FioczPipeline': 300,
    }
    url_list = []

    def parse(self, response):
        post_links = response.xpath('//h6/a/@href').getall()

        for url in post_links:
            if url in self.url_list:
                raise CloseSpider('no more pages')
            self.url_list.append(url)
            yield response.follow(url, self.parse_post)

        next_page = 'https://www.fio.cz/about-us/media/press-releases?offset={}'
        if len(post_links) == 12:
            self.offset += 12
            yield response.follow(next_page.format(self.offset), self.parse)

    def parse_post(self, response):
        date = response.xpath('//p[@class="meta"]/text()').get().strip().split(' ')[0]
        title = response.xpath('//h1/text()').get()
        content = response.xpath(
            '//div[@class="section3 newsSection"]//text()[not (ancestor::p[@class="meta"])]').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=FioczItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

