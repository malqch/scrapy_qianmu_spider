# -*- coding: utf-8 -*-
import scrapy
from qianmu.items import UniversityItem

class UniversitySpider(scrapy.Spider):
    name = 'university'
    allowed_domains = ['qianmu.iguye.com']
    start_urls = ['http://qianmu.iguye.com/2018USNEWS%E4%B8%96%E7%95%8C%E5%A4%A7%E5%AD%A6%E6%8E%92%E5%90%8D']

    def __init__(self, max_num=0, *args, **kwargs):
        super(UniversitySpider, self).__init__(*args, **kwargs)
        self.max_num = int(max_num)

    def parse(self, response):
        links = response.xpath("//*[@id='content']/table/tbody/tr/td[2]/a/@href").extract()
        for i, link in enumerate(links):
            if self.max_num and self.max_num <= i:
                break
            if not link.startswith('http://'):
                link = 'http://qianmu.iguye.com/%s' % link
            # yield response.follow(link, callback=)
            request = scrapy.Request(link, callback=self.parse_university)
            request.meta['rank'] = i + 1
            yield request

    def parse_university(self, response):
        response = response.replace(body=response.text.replace('\t', ''))
        self.logger.info(response.url)
        item = UniversityItem(
            name=response.xpath("//*[@id='wikiContent']/h1/text()").extract_first(),
            rank=response.meta['rank'],
        )
        wiki_content = response.xpath("//div[@class='infobox']")[0]
        # item = dict(title=response.xpath("//*[@id='wikiContent']/h1/text()").extract_first())
        # item['rank'] = response.meta['rank']
        keys = wiki_content.xpath("./table//tr/td[1]/p/text()").extract()
        colums = wiki_content.xpath("./table//tr/td[2]")
        values = [''.join(col.xpath('.//text()').extract()) for col in colums]
        data = dict(zip(keys, values))
        item['country'] = data.get('国家', '')
        item['state'] = data.get('州省', '')
        item['city'] = data.get('城市', '')
        item['undergraduate_num'] = data.get('本科生人数', '')
        item['postgraduate_num'] = data.get('研究生人数', '')
        item['website'] = data.get('网址', '')
        # item.update(zip(keys, values))
        self.logger.info('item %s scraped' % item['name'])
        yield item