import tornado.web
import tornado.gen
import json

from models import OrderBook

from utils import get_orders, get_rate, find_order, deal


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        self.application.db.connect()
        return self.application.db


class MainHandler(BaseHandler):
    async def get(self):
        rate = await get_rate(self.db)
        orders = await get_orders(self.db)

        self.render("order_form.html", current_bitcoin_rate=rate, orders=orders)

    async def post(self, *args, **kwargs):
        order_type = 'buy' if 'buy' in self.request.arguments else 'sell'
        price = float(self.get_argument('price', .0))
        count = float(self.get_argument('count', .0))
        current_order = OrderBook(status=1, price_per_item=price, count=count,
                                  order_type=order_type)

        rate = await get_rate(self.db)
        orders = await get_orders(self.db)

        orders.append(current_order.__dict__)

        orders.sort(key=lambda x: x['order_type'], reverse=True)
        orders.sort(key=lambda x: x['price_per_item'], reverse=True)

        #find_order(current_order)
        await tornado.gen.Task(self.db.set, 'orders', json.dumps(orders))

        self.render("order_form.html", current_bitcoin_rate=rate, orders=orders)
