
![](http://p20tr36iw.bkt.clouddn.com/guazi.png)

<!--more-->

# 瓜子二手车抓手

## 0.说在前面

本次爬虫抓取瓜子二手车信息，包括车型及价格！

你可以学到？

- cookie的作用
- 多页面信息爬取
- xpath使用
- 两大数据库操作

那么接下来进入分析环节。

## 1.网页分析

网页地址为:`https://www.guazi.com/cq/buy`

分析难点:

- cookie,自己加入浏览器上的cookie，然后即可运行，需要填写下面的mysql数据库密码！
- 多页面处理

`https://www.guazi.com/cq/buy/o2/#bread`

分析发现，多页面不同之处在于'o2'处，这里的2即为和页数，也就是说我只需要拿到页面的总页数，循环遍历即可，这就是本爬虫的核心思路，那么怎么拿到呢？看下图：

![](http://p20tr36iw.bkt.clouddn.com/guazi.png)

会发现，总页数在导数第二个li标签，那么通过xpath定位，在返回的list中去导数第二个即为总页面数！

这里需要注意，到了最后一个页面399时候，就不会出现下一页，此时399即为最后一个li标签，那么在xpath使用的时候，只需要用第一个页面的url获取总页面数即可！

## 2.功能实现

- 导包

```python
import pymysql
import requests
from lxml import etree
import pymongo
```

- 类封装

```python
class guazi_spider(object):
```

**注意:**以下所有的方法封装在本类中！

- 初始化类方法

```python
def __init__(self,mongo_uri,mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
```

- 获取当前页面源码

```python
def get_html(self,url):
        headers = {
            'Cookie': '填写自己的cookie'
        }
        raw_html = requests.get(url, headers=headers).text
        return raw_html
```

- 获取页面数量

```python
def get_PageNumber(self):
        url = 'https://www.guazi.com/cq/buy/'
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        # 获取页面总数
        page_total = selector.xpath('//ul[@class="pageLink clearfix"]//li//span/text()')[-2]
        return  page_total
```

- 获取页面数据

```python
def get_AllPage(self,url):
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        # 汽车型号
        car_name = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//h2/text()')
        # 汽车价格
        car_price = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//div[@class="t-price"]//p/text()')
        return car_name,car_price
```

- mongodb存储

```python
def Save_MongoDB(self,data):
        self.db[MONGO_COLLECTION].insert_one(data)
        self.client.close()
```

- mysql存储

```python
def Save_Mysql(self,car_name,car_price):
        # 填写数据库密码
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
```

## 3.调用呈现

- 调用

```python
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
```

- mysql 数据

![](http://p20tr36iw.bkt.clouddn.com/car_mysql.png)

- mongodb数据

![](http://p20tr36iw.bkt.clouddn.com/car_mongodb.png)

- 终端

![](http://p20tr36iw.bkt.clouddn.com/car_terminal.png)

- 验证数据

**mysql与mongodb数据量计算：**

mysql中我们看到上图为第16页数据，当前页937条数据，而前15页为1000条，那么总共爬取到了15937条。对于mongodb数据而言，我们看到共399页数据，每页数据即为原网页的数据，除了最后一页为17条，前398页面中每一页有40条，那么计算公式为：398*40+17 = 15937条数据！两个数据库最终计算一致，说明无误！为了再此验证准确性，特拿出原网页的后面几条数据与两个数据库的最后几条数据对比，原网页最后页面如下:

![](http://p20tr36iw.bkt.clouddn.com/last_car.png)

将这副图与上述两个数据库的最后数据比对，验证也正确！

**最后：网站数据是动态的，我爬取到的数据量与你爬取的不一定一致，请掌握方法即可！**



## 4. 项目地址

[戳这里!!!](https://github.com/Light-City/guazi)

