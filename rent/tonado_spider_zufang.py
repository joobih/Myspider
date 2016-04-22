#encoding=utf-8

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import ioloop, gen, queues
from bs4 import BeautifulSoup
import time
import re
from collections import OrderedDict
from zufang import url_tools

g_q = queues.Queue() 
fetching,fetched = OrderedDict(),OrderedDict()

#下载url网页
@gen.coroutine
def zufang_spider(url):
    response = yield AsyncHTTPClient().fetch(url,raise_error = False)
    raise gen.Return(response)
    
def headers_func(value):
        print(value,"value")
    
@gen.coroutine
def run():
    try:
        url = yield g_q.get()
        fetched[url] = 1
        request = HTTPRequest(url)
        res = yield zufang_spider(request)
        html = res.body
        zufang_info(url, html)
    finally:
        g_q.task_done()

@gen.coroutine
def worker():
    while not g_q.empty():
        yield run()

def add_sub_url(url, html):
    bs = BeautifulSoup(html,"html.parser")
    urls = []
    a_tag = bs.find_all("a")
    host = url_tools.get_url_http(url)
    for a in a_tag:
        href = a.get("href")
        if href:
            http_ = re.compile("http", flags=0)
            result = re.search(http_, href, flags=0)
            if result:
                urls.append(href)
            elif href[0] == "/":
                urls.append(host+href)
                print(href)
    return urls

#获取data中的租房的基本信息    
def zufang_info(url, data):
    bs = BeautifulSoup(data,"html.parser")
    url_list = add_sub_url(url, data.decode())
    print(url_list)
    title_class = "main-title font-heiti"
    price_class = "house-primary-content-li house-primary-content-fir clearfix"
    normal_class = "house-primary-content-li clearfix"
    normal_house_class = "fl house-type c70"
    normal_xiaoqu_class = "fl xiaoqu c70"
    normal_address_class = "fl c70"
    price_class_div = "fl"
    price_class_i = "ncolor"
    title_bs = bs.find(attrs={"class":title_class})
    if not title_bs:
        return None
    title = title_bs.get_text()
    price_bs = bs.find(attrs={"class":price_class})
    price_div = price_bs.find(attrs={"class":price_class_div})
    price_i = price_bs.find(attrs={"class":price_class_i})
    price_i = price_i.get_text()
    price_text = price_div.get_text()+''.join([price_i])
    price = price_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    normal_bs = bs.find_all(attrs={"class":normal_class})
    normal_house__bs = normal_bs[0].find(attrs={"class":normal_house_class})
    normal_xiaoqu_bs = normal_bs[1].find(attrs={"class":normal_xiaoqu_class})
    normal_address_bs = normal_bs[2].find(attrs={"class":normal_address_class})
    house_text = normal_house__bs.get_text()
    house = house_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    house = "房屋：" + house
    xiaoqu_text = normal_xiaoqu_bs.get_text()
    xiaoqu = xiaoqu_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    xiaoqu = "小区："  + xiaoqu
    address_text = normal_address_bs.get_text()
    address = address_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    address = "地址：" + address
#     print(title)
#     print(price)
#     print(house)
#     print(xiaoqu)
#     print(address)

@gen.coroutine
def main():
    for _ in range(0,1):    # 放100个链接进去
        url = "http://sh.58.com/zufang/25694336686763x.shtml" 
        yield g_q.put(url)
        fetching[url] = 1
    for _ in range(0,1):    # 模拟100个线程 
        worker()
    yield g_q.join()

if __name__ == '__main__':
    start_time = time.time()
    ioloop.IOLoop.current().run_sync(main)
    end_time = time.time()
    print(end_time-start_time)
    print(fetching)
    print(fetched)