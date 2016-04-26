#encoding=utf-8
import os.path
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.httpclient
from tornado.options import define, options

define('port', default = 8100, help='run on the given port', type=int)

def caback(response):
    print response,"response"

class AsynHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        try:
        	#这里的fetch函数会在执行完过后将抓取到的数据set_result到future中。这时候就会执行run，
        	#run里面会send结果返回回来。
            rsp = yield client.fetch('https://www.baidu.com/')#, callback = caback)
        except:
            pass
        self.write('server return')
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/tor_test', AsynHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "templates")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port)
    http_server.start(4)
#    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()        