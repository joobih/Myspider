#encoding=utf-8

import time
import threading
import threadpool
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

#下载url网页
def zufang_spider(url):
    req = urllib.request.Request(url)
    data = urllib.request.urlopen(req)
    host = req.get_header("Host")
    data = data.read()
    print(host)
    data = data.decode()
    return data
    
#获取data中的租房的基本信息    
def zufang_info(data):
    bs = BeautifulSoup(data,"html.parser")
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
        return
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
    print(title)
#     print(price)
#     print(house)
#     print(xiaoqu)
#     print(address)

def zufang(u):
    data = zufang_spider(u)
    zufang_info(data)

# url = "http://sh.58.com/zufang/25694336686763x.shtml"
url = "https://www.aliyun.com/product/rds/postgresql?utm_medium=text&utm_source=baidu&utm_campaign=postgresql&utm_content=se_241880"
url_list = []
for i in range(0,10):
    url_list.append(url)
start_time = time.time()
# threads = []
poll = threadpool.ThreadPool(100)
reqs = threadpool.makeRequests(zufang,url_list)
[poll.putRequest(req) for req in reqs]
poll.wait()
# for i in range(0,1000):
#     t = threading.Thread(target=zufang)
#     threads.append(t)
#     t.start()
# for i in range(0,1000):
#     threads[i].join()
end_time = time.time()
print("开了线程耗时：",end_time-start_time)

# for i in range(0,100):
#     zufang()
# end_time2 = time.time()
# print("没开线程时耗时：",end_time2-end_time)
