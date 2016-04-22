#encoding=utf-8
import tornado.ioloop
from my58_com import spider_prepare
from tornado import queues,gen
import time

_q = queues.Queue()

@gen.coroutine
def main():
    spider_prepare.logging.info("start fetch url")
    hosts = ["http://www.58.com","http://cd.58.com"]
    file_name = "urls.txt"
    spider_prepare.set_base_urls(_q, hosts)
    for i in range(0,100):
        #获取1000个url
        spider_prepare.get_url_queue(_q,hosts,10000,file_name)
#         spider_prepare.write_urls_to_file(file_name,100)
#     yield _q.join()
    print("over")
#     file_name = "urls.txt"
#     spider_prepare.write_urls_to_file(file_name)
    yield _q.join()
    
if __name__ == '__main__':
    start_time = time.time()
    tornado.ioloop.IOLoop.current().run_sync(main)
    end_time = time.time()
    print(end_time-start_time)
    
