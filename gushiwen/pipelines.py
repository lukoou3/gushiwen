# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from gushiwen.items import GushiwenItem,AuthorItem,ZztjItem

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

class ZztjPipeline(object):
    def process_item(self, item, spider):
        db = spider.db
        if isinstance(item,ZztjItem):
            tb = db.zztj
            tb.update_one({"_id": item["_id"]},{"$set":item}, upsert=True)
        return item

"""
import pymongo
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database("gushiwen")
[(line,item["title"])  for item in sorted(db.gushiwen.find({},{"contents":1,"title":1,"good":1,"_id":-1}),
key=lambda item:int(item['good']),reverse=True) for line in item["contents"] if "酒" in line and len(line) < 80]
"""