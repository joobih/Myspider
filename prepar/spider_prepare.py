#encoding=utf-8

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import gen
from bs4 import BeautifulSoup
import time
import re
from collections import OrderedDict
from zufang import url_tools
import collections
import logging
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='spider.log',
                    filemode='w')

fetch = OrderedDict()
collected = collections.deque()

#下载url网页
@gen.coroutine
def fetch_58(request):
    response = yield AsyncHTTPClient().fetch(request,raise_error = False)
    raise gen.Return(response)

def get_from_deque():
    url = None
    if collected:
        url = collected.pop()
#         print("pop:",url)
    return url

@gen.coroutine
def set_base_urls(queue,urls):
    for url in urls:
        fetch[url] = 1
        collected.append(url)
        yield queue.put(url)

@gen.coroutine
def set_urls(queue,urls,hosts):
    for url in urls:
        if url in fetch:
            continue
        host = url_tools.get_url_http(url)
        if host == '':
            logging.error("set_urls:get url host none url:%s" % url)
            continue
        if host not in hosts:
            continue
        fetch[url] = 1
        collected.append(url)
        yield queue.put(url)

@gen.coroutine
def run(queue,base_hosts):
    try:
        url = get_from_deque()
        request = HTTPRequest(url,request_timeout=1.0)
        res = yield fetch_58(request)
        html = res.body
        st = time.time()
#         print("return",url)
#         print("-----------")
        if html:
            add_sub_url_to_q(queue, url, html,base_hosts)
        else:
            print("html",url,"None")
        en = time.time()
#         print(en-st)
    except Exception as e:
        logging.error("fetch url:%s.except:%s" % (url,str(e)))
    finally:
        pass

#只关心hosts中提到的域名地址。其他地址直接忽略。若没设置该值，则页面中所有的url地址都会被保存
def get_sub_urls_from_html(url,html,hosts = []):
    try:
        bs = BeautifulSoup(html,"html.parser")
        urls = []
        a_tag = bs.find_all("a")
        host = url_tools.get_url_http(url)
        if host not in hosts:
            return urls
        for a in a_tag:
            href = a.get("href")
            if href:
                url_re = re.compile("(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?", flags = 0)
                result = re.match(url_re, href, flags = 0)
                if result:
                    urls.append(href)
                elif href[0] == "/":
                    urls.append(host+href)
        return urls
    except Exception as e:
        logging.error("get_sub_urls_from_html at url %s, occure a except:%s" % (url, str(e)))
        return []
        
@gen.coroutine
def add_sub_url_to_q(q, url, html,hosts=[]):
    urls = get_sub_urls_from_html(url,html,hosts)
    set_urls(q,urls,hosts)

@gen.coroutine
def get_url_queue(q,hosts,count,file_name):
    len_c = len(fetch)
    while not q.empty() and len_c < count:
        yield run(q, hosts)
        len_c = len(fetch)
    print("get_url_queue")
    write_urls_to_file(file_name,count)
    print("write_to file")
        
def write_urls_to_file(file_name,count):
#     f = open(file_name,"w+")
    if len(fetch)<count:
        return
    f = open(file_name,"w+")
    for url in fetch:
        f.write(url+"\n")
#     print(fetch)