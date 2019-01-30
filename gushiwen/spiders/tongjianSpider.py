# -*- coding: utf-8 -*-
import scrapy
from scrapy import cmdline
from gushiwen.items import ZztjItem
import pymongo

class TongJianSpider(scrapy.Spider):
    name = 'zztj'
    allowed_domains = ['www.artx.cn','guji.artx.cn']
    start_urls = ['http://www.artx.cn/user/login.asp?act=submit&duser=lukou3&dpwd=l184521']
    custom_settings = {
        'ITEM_PIPELINES': {
            'gushiwen1.pipelines.ZztjPipeline': 300,
        }
    }

    def __init__(self,*args, **kwargs):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.gushiwen
        self.zztj_ids = {item["_id"] for item in self.db.zztj.find()}
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], dont_filter=True)

    def parse(self, response):
        yield scrapy.Request("http://guji.artx.cn/article/43860.html",callback=self.parseZztj)

    def parseZztj(self, response):
        links = response.xpath("//div[@class='l_mulu_td']//li/a")
        for i,link in enumerate(links,start=1):
            item = ZztjItem()
            item['_id'] = i
            item['title'] = link.xpath("./text()").get()
            if item['_id'] in self.zztj_ids:
                continue
            yield scrapy.Request(response.urljoin(link.xpath("./@href").get()), meta={"item": item}, callback=self.parseContent)
    def parseContent(self, response):
        item = response.meta['item']
        item['content'] = response.xpath("//div[@id='r_zhengwen']").get()
        yield item

    def closed(self,*args):
        self.client.close()

if __name__ == "__main__":
    cmdline.execute("scrapy crawl zztj".split())
