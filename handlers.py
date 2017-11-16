import tornado.web
import tornado.gen
from tornado.escape import json_decode
from tornado import httpclient


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        self.application.db.connect()
        return self.application.db


class MainHandler(BaseHandler):
    async def get(self):
        http_client = httpclient.AsyncHTTPClient()
        rate = await tornado.gen.Task(self.db.get, 'rate')
        if rate:
            self.render("base.html", current_bitcoin_rate=rate)
        else:
            r = await http_client.fetch("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
            decoded = json_decode(r.body)
            rate = decoded['bpi']['USD']['rate_float']
            if not rate:
                raise tornado.web.HTTPError(404)
            await tornado.gen.Task(self.db.set, 'rate', rate, 60)
            self.render("base.html", current_bitcoin_rate=rate)

    async def post(self, *args, **kwargs):
        pass