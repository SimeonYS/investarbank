import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IinvestarbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IinvestarbankSpider(scrapy.Spider):
	name = 'investarbank'
	start_urls = ['https://investors.investarbank.com/websites/investar-bank/English/2100/press-releases.html?page=1&items_per_page=10']

	def parse(self, response):
		post_links = response.xpath('//div[@class="newslist__wrapper"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="page-link pl-03"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//h6/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="content"]//text()[not (ancestor::h1 or ancestor::h6 or ancestor::div[@class="go-back"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=IinvestarbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
