# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GushiwenItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field()
    dynasty = scrapy.Field()
    author = scrapy.Field()
    contents = scrapy.Field()
    good = scrapy.Field()
    tags = scrapy.Field()
    play_url = scrapy.Field()
    play_author = scrapy.Field()
    yizhu_cont = scrapy.Field()
    yizhu_yi = scrapy.Field()
    yizhu_zhu = scrapy.Field()
    yizhu_yizhu = scrapy.Field()
    yizhu_shang = scrapy.Field()
    beijings = scrapy.Field()

class AuthorItem(scrapy.Item):
    name = scrapy.Field()
    dynasty = scrapy.Field()
    info = scrapy.Field()

class ZztjItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()