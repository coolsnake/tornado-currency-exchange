import os

import tornado.web
import tornado.httpserver
import tornado.gen
import tornado.ioloop
import tornado.options
import tornadoredis
from tornado.options import define, options

from handlers import MainHandler


define('port', default=8888, type=int, help="Run on the given port")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        super(Application, self).__init__(handlers, **settings)

        self.db = tornadoredis.Client()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address='0.0.0.0')
    tornado.ioloop.IOLoop.current().start()
