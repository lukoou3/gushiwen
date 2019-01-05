# -*- coding: utf-8 -*-
import scrapy
from gushiwen.items import GushiwenItem,AuthorItem
from scrapy import cmdline
import re
import pymongo

class GushiwenSpider(scrapy.Spider):
    name = 'shiwen'
    allowed_domains = ['www.gushiwen.org', 'so.gushiwen.org']
    start_urls = ['https://so.gushiwen.org/user/collect.aspx']
    cookies = {'ASP.NET_SessionId': 'uwf01hilkd4oyh4acxkvw5kr', 'gsw2017user': '255194%7cF6405B74D299A699ABD2E5DDED431F63', 'gswEmail': '18638489474%40163.com', 'sec_tc': 'AQAAAFOYXFaP8AoAcvuDkm6mVkcrl715', 'idsShiwen2017': '%2c71200%2c18709%2c19003%2c71284%2c18998%2c19002%2c19032%2c18997%2c18515%2c71248%2c27845%2c27620%2c27713%2c27824%2c27709%2c47915%2c27724%2c27721%2c70845%2c27763%2c71208%2c21744%2c22550%2c21818%2c2077%2c21287%2c21173%2c21750%2c22492%2c22098%2c21838%2c22150%2c47085%2c22907%2c71053%2c7722%2c7816%2c8086%2c70874%2c71193%2c8014%2c8156%2c8027%2c7717%2c8488%2c8328%2c8089%2c70862%2c7766%2c8481%2c8345%2c7826%2c7741%2c8337%2c8180%2c8411%2c1744%2c8279%2c8066%2c7727%2c2025%2c47070%2c71217%2c7822%2c47069%2c8407%2c7914%2c70872%2c70878%2c7787%2c57601%2c57913%2c57678%2c57611%2c58029%2c57989%2c57795%2c57580%2c57521%2c57515%2c10835%2c10521%2c10968%2c10374%2c71194%2c11064%2c10449%2c11098%2c71198%2c10886%2c10928%2c11532%2c11550%2c11245%2c11010%2c71938%2c11149%2c10388%2c10965%2c70838%2c71074%2c71076%2c47040%2c47045%2c47057%2c65087%2c47053%2c71995%2c71706%2c71492%2c5122%2c70849%2c48248%2c48269%2c48343%2c48358%2c48401%2c48305%2c', 'Hm_lvt_04660099568f561a75456483228a9516': '1545614420,1545704338,1546044670,1546070936', 'Hm_lpvt_04660099568f561a75456483228a9516': '1546070942'}
    re_playjs = re.compile(r"Play\((\d+)\)")
    re_shang = re.compile(r""".*?<div class="hr"></div>(.*)""",re.DOTALL)
    re_shang_img = re.compile(r"/img/([a-z]*)pic\.png")
    re_link_a = re.compile(r"<a.+?>(.+?)</a>")
    yizhu_items = ('cont','yi','zhu','yizhu','shang')

    def __init__(self,*args, **kwargs):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.gushiwen
        self.gushiwen_ids = {item["_id"] for item in self.db.gushiwen.find()}
        self.gushiwen_authors = {(item["dynasty"],item["name"]) for item in self.db.gushiwen_author.find()}
        #tb = self.db.gushiwen
        #tb.create_index('title', unique=True)
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], cookies=self.cookies, dont_filter=True)

    def parse(self, response):
        divs = response.xpath("//div[@class='left']/div[@class='sons']")
        for div in divs:
            item = GushiwenItem()
            item['title'] = div.xpath(".//div[@class='yizhu']/following-sibling::p[1]//text()")[0].extract()
            item['dynasty'] = div.xpath(".//p[@class='source']/a[1]/text()")[0].extract()
            item['author'] = div.xpath(".//p[@class='source']/a[2]/text()")[0].extract()
            item['_id'] = div.xpath(".//div[@class='contson']/@id").get()[7:]
            item['contents'] = [line.strip() for line in div.xpath(".//div[@class='contson']//text()").extract() if line.strip() != ""]
            item['good'] = div.xpath("./div[@class='tool']//div[@class='good']//text()").get().strip()
            item['tags'] = div.xpath(".//div[@class='tag']/a/text()").getall()

            if (item["dynasty"],item["author"]) not in self.gushiwen_authors:
                yield scrapy.Request(response.urljoin("/search.aspx?value={}".format(item['author'])),
                        meta={"author": item['author'],"dynasty": item['dynasty']},callback=self.parse_author)

            if item['_id'] in self.gushiwen_ids:
                continue

            yizhu_imgs = div.xpath(".//div[@class='yizhu']/img[position()>1]")
            yizhu_imgs = [yizhu_img.xpath("./@src").get() for yizhu_img in yizhu_imgs if div.get().count(yizhu_img.xpath("./@id").get())==2]
            yizhu_imgs = [self.re_shang_img.search(yizhu_img).group(1) for yizhu_img in yizhu_imgs]
            if 'zhu' in yizhu_imgs and 'yi' in yizhu_imgs:
                yizhu_imgs.append("yizhu")
            yizhu_imgs.append("cont")
            yizhu_list = tuple(("yizhu_"+yizhu,"/shiwen2017/ajaxshiwencont.aspx?id={}&value={}".format(item['_id'],yizhu))
                          for yizhu in yizhu_imgs)
            jsstr = div.xpath("./div[@class='tool']//a[contains(@href,'Play(')]/@href").get()
            if jsstr:
                match = self.re_playjs.search(jsstr)
                play_id = match.group(1)
                play_query_url = response.urljoin("/viewplay.aspx?id={}".format(play_id))
                yield scrapy.Request(play_query_url, meta={"item": item,"yizhu_list":yizhu_list}, callback=self.parse_play_url)
            else:
                yield scrapy.Request(response.urljoin(yizhu_list[0][1]), meta={"item": item,"yizhu_list":yizhu_list}, callback=self.parse_yi_zhu)
        next_href = response.xpath("//div[@class='pagesright']/a[@class='amore']/@href").get()
        if next_href:
            yield  scrapy.Request(response.urljoin(next_href),callback=self.parse)

    def parse_play_url(self, response):
        item = response.meta['item']
        yizhu_list = response.meta['yizhu_list']
        item['play_url'] = response.xpath("//audio/@src").get()
        item['play_author'] = response.xpath("//a[contains(@href,'song/author')]/text()").get()
        yield scrapy.Request(response.urljoin(yizhu_list[0][1]), meta={"item": item, "yizhu_list": yizhu_list},
                             callback=self.parse_yi_zhu)

    def parse_yi_zhu(self, response):
        item = response.meta['item']
        yizhu_list = response.meta['yizhu_list']
        if yizhu_list[0][0] != "yizhu_shang":
            item[yizhu_list[0][0]] = response.text
        else:
            #siblings = response.xpath("//div[@class='hr']/following-sibling::*")
            #siblings.getall()
            match = self.re_shang.search(response.text)
            if match:
                text = match.group(1)
            else:
                text = response.text
            item[yizhu_list[0][0]] = text
        if len(yizhu_list) > 1:
            yizhu_list = yizhu_list[1:]
            yield scrapy.Request(response.urljoin(yizhu_list[0][1]), meta={"item": item, "yizhu_list": yizhu_list},
                                 callback=self.parse_yi_zhu)
        else:
            yield scrapy.Request(response.urljoin("/shiwenv_{}.aspx".format(item['_id'])),
                                 meta={"item": item},callback=self.parse_info)

    def parse_info(self, response):
        item = response.meta['item']
        beijings = []
        divs = response.xpath("//div[@class='contyishang' and (contains(.//h2//text(),'背景') or contains(.//h2//text(),'解说'))]")
        for div in divs:
            title = div.xpath(".//h2//text()").get()
            if div.xpath("./p"):
                ps = self.re_link_a.sub(r"\1","".join(div.xpath("./p").getall()))
            else:
                ps = "".join(div.xpath(".//text()").getall()).strip().replace(title,"")
            beijings.append({"title":title,"cont":ps})
        item["beijings"] = beijings
        yield item

    def parse_author(self, response):
        name = response.meta['author']
        dynasty = response.meta['dynasty']
        texts = response.xpath("//div[@class='sonspic']/div[@class='cont']/p[last()]//text()").getall()
        info = "".join(texts).strip()
        item = AuthorItem({"name":name,"dynasty":dynasty,"info":info})
        yield item

    def closed(self,*args):
        print("#"*40)
        self.client.close()
        print("#"*40)

if __name__ == "__main__":
    cmdline.execute("scrapy crawl shiwen".split())
