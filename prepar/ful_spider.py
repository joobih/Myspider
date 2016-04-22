#encoding=utf-8

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import ioloop, gen, queues
from bs4 import BeautifulSoup
import time
import re
from collections import OrderedDict
# from html.parser import HTMLParser
from zufang import url_tools

g_q = queues.Queue() 
fetching,fetched = OrderedDict(),OrderedDict()

#下载url网页
@gen.coroutine
def fetch_58(url):
    response = yield AsyncHTTPClient().fetch(url,raise_error = False)
    raise gen.Return(response)

@gen.coroutine
def run():
    try:
        url = yield g_q.get()
        fetched[url] = 1
        print(url)
        request = HTTPRequest(url)
        res = yield fetch_58(request)
        html = res.body
        st = time.time()
        print("-----------")
        zufang_info(url, html)
        en = time.time()
        print(en-st)
    finally:
        g_q.task_done()

@gen.coroutine
def worker():
    while not g_q.empty():
        yield run()

def get_sub_url(url, bs):
    urls = []
    a_tag = bs.find_all("a")
    host = url_tools.get_url_http(url)
    if host not in ("http://sh.58.com","http://www.58.com"):
        return urls
    for a in a_tag:
        href = a.get("href")
        if href:
            http_ = re.compile("http", flags=0)
            result = re.search(http_, href, flags=0)
            if result:
                urls.append(href)
            elif href[0] == "/":
                urls.append(host+href)
    return urls

@gen.coroutine
def add_queue(urls):
#     print(urls)
    for u in urls:
        if u in fetched or u in fetching:
            continue
        yield g_q.put(u)
        fetching[u] = 1

#获取data中的租房的基本信息    
@gen.coroutine
def zufang_info(url, data):
#     start = time.time()
    bs = BeautifulSoup(data,"html.parser")
#     start = time.time()
    url_list = get_sub_url(url, bs)
#     end = time.time()
    start = time.time()
    yield add_queue(url_list)
    end = time.time()
#     print("deal get_sub_url time:",end-start)
    if end-start >1:
        print("超过1秒:",url)
    title_class = "main-title font-heiti"
    price_class = "house-primary-content-li house-primary-content-fir clearfix"
    normal_class = "house-primary-content-li clearfix" #包含房屋，小区，地区
    furniture_li = "house-primary-content-li clearfix broken-config"
#     furniture_span = "fl pr20 c2e"
#     furniture_span_1 = "inlineblock"
    normal_house_class = "fl house-type c70"
    normal_xiaoqu_class = "fl xiaoqu c70"
    normal_address_class = "fl c70"
    price_class_div = "fl"
    price_class_i = "ncolor"
    title_bs = bs.find(attrs={"class":title_class})
    if not title_bs:
#         print(url)
        return None
    print(url)
    title = title_bs.get_text()
    price_bs = bs.find(attrs={"class":price_class})
    price_div = price_bs.find(attrs={"class":price_class_div})
    price_i = price_bs.find(attrs={"class":price_class_i})
    price_i = price_i.get_text()
    price_text = price_div.get_text()+''.join([price_i])
    price = price_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    normal_bs = bs.find_all(attrs={"class":normal_class})
    try:
#         if len(normal_bs) == 3:
        normal_house__bs = normal_bs[0].find(attrs={"class":normal_house_class})
        normal_xiaoqu_bs = normal_bs[1].find(attrs={"class":normal_xiaoqu_class})
        if len(normal_bs) == 3:
            normal_address_bs = normal_bs[2].find(attrs={"class":normal_address_class})
        else:
            normal_address_bs = None
    except Exception as e:
        print(e)
        print(url,"url")
    house_text = normal_house__bs.get_text()
    house = house_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    house = "房屋：" + house
    xiaoqu_text = normal_xiaoqu_bs.get_text()
    xiaoqu = xiaoqu_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
    xiaoqu = "小区："  + xiaoqu
    address = None
    if normal_address_bs:
        address_text = normal_address_bs.get_text()
        address = address_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
        address = "地址：" + address
        
    furniture_bs = bs.find(attrs={"class":furniture_li})
    if furniture_bs:
        furniture_text = furniture_bs.get_text()
        furniture = furniture_text.replace(" ","").replace("\t","").replace("\n","").replace("\r","")
        print(furniture)
    
    print(title)
    print(price)
    print(house)
    print(xiaoqu)
    print(address)

def add_url_to_queue(base_url):
    pass

@gen.coroutine
def main():
#     add_url_to_queue(base_url)
    for _ in range(0,1):    # 放100个链接进去
#         url = "http://sh.58.com" 
#         url = "http://sh.58.com/zufang/25694336686763x.shtml"
        url = "http://sh.58.com/beicai/zufang/?PGTID=0d400008-0061-4896-fef3-47b81f320fbf&ClickID=5"
        yield g_q.put(url)
        fetching[url] = 1
    for _ in range(0,100):    # 模拟100个线程 
        worker()
    yield g_q.join()

if __name__ == '__main__':
    start_time = time.time()
    ioloop.IOLoop.current().run_sync(main)
    end_time = time.time()
    print(end_time-start_time)
    print(fetching)
    print(fetched)