import pymysql
import requests
from lxml import etree
import pymongo

MONGO_URI = 'localhost'
MONGO_DB = 'test' # 定义数据库
MONGO_COLLECTION = 'guazi' # 定义数据库表

class guazi_spider(object):
    def __init__(self,mongo_uri,mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def get_html(self,url):
        headers = {
            'Cookie':'填写你的cookie',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        raw_html = requests.get(url, headers=headers).text
        return raw_html

    def get_PageNumber(self):
        url = 'https://www.guazi.com/cq/buy/'
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        page_total = selector.xpath('//ul[@class="pageLink clearfix"]//li//span/text()')[-2]
        return  page_total

    def get_AllPage(self,url):
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        car_name = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//h2/text()')
        car_price = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//div[@class="t-price"]//p/text()')
        return car_name,car_price

    def Save_MongoDB(self,data):
        self.db[MONGO_COLLECTION].insert_one(data)
        self.client.close()

    def Save_Mysql(self,car_name,car_price):
        connection = pymysql.connect(host='localhost', user='root', password='xxx', db='scrapydb',
                                     charset='utf8mb4')
        try:
            for i in range(len(car_name)):
                with connection.cursor() as cursor:
                    sql = "insert into `guazi`(`汽车型号`,`汽车价格`)values(%s,%s)"
                    cursor.execute(sql, (car_name[i], car_price[i]))
            connection.commit()
        finally:
            connection.close()

guazi = guazi_spider(MONGO_URI,MONGO_DB)

page_total = guazi.get_PageNumber()
for page in range(1,int(page_total) + 1):
    print("-----第" + str(page) + "页爬取开始------")
    guazi_data = {}
    url = 'https://www.guazi.com/cq/buy/o' + str(page) + '/#bread'
    car_name,car_price = guazi.get_AllPage(url)
    print(car_name)
    print(car_price)
    guazi_data["汽车型号"] = car_name
    guazi_data["汽车价格"] = car_price
    guazi.Save_MongoDB(guazi_data)
    print(guazi_data)
    guazi.Save_Mysql(car_name,car_price)
    print("-----第" + str(page) + "页爬取结束------")

print("------爬虫结束------")

