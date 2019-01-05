# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from gushiwen.items import GushiwenItem,AuthorItem

class GushiwenPipeline(object):
    def process_item(self, item, spider):
        db = spider.db
        if isinstance(item,GushiwenItem):
            tb = db.gushiwen
            #tb.insert_one(item)
            tb.update_one({"_id": item["_id"]},{"$set":item}, upsert=True)
        elif isinstance(item,AuthorItem):
            tb = db.gushiwen_author
            #tb.insert_one(item)
            tb.update_one({"name": item["name"],"dynasty": item["dynasty"]},{"$set":item}, upsert=True)
        return item
