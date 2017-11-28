import tornado.web
import tornado.gen
import json

from models import OrderBook

from utils import get_orders, get_rate, build_order_book


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        self.application.db.connect()
        return self.application.db


class MainHandler(BaseHandler):
    async def get(self):
        rate = await get_rate(self.db)
        sell_orders = await get_orders(self.db, type='sell')
        buy_orders = await get_orders(self.db, type='buy')

        self.render("order_book.html", current_bitcoin_rate=rate, sell_orders=sell_orders,
                    buy_orders=buy_orders)

    async def post(self, *args, **kwargs):
        price = float(self.get_argument('price', .0))
        count = float(self.get_argument('count', .0))
        current_order = OrderBook(status=1, price_per_item=price, count=count)

        order_type = 'buy' if 'buy' in self.request.arguments else 'sell'  # костыль self.get_argument
        await build_order_book(order_type, current_order, self.db)
        rate = await get_rate(self.db)
        sell_orders = await get_orders(self.db, type='sell')
        buy_orders = await get_orders(self.db, type='buy')
        self.render("order_book.html", current_bitcoin_rate=rate, sell_orders=sell_orders,
                    buy_orders=buy_orders)
