import tornado.web
import tornado.gen
from tornado.escape import json_decode
from tornado import httpclient
import json

from models import OrderBook


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        self.application.db.connect()
        return self.application.db


class MainHandler(BaseHandler):
    async def get(self):
        rate = await tornado.gen.Task(self.db.get, 'rate')
        if rate:
            self.render("order_form.html", current_bitcoin_rate=rate)
        else:
            http_client = httpclient.AsyncHTTPClient()
            try:
                api_response = await http_client.fetch("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
                decoded = json_decode(api_response.body)
                rate = decoded['bpi']['USD']['rate_float']
            except httpclient.HTTPError as e:
                print("Error: " + str(e))
            except Exception as e:
                print("Error: " + str(e))
            http_client.close()
            if not rate:
                raise tornado.web.HTTPError(404)
            await tornado.gen.Task(self.db.set, 'rate', rate, 60)
            self.render("order_form.html", current_bitcoin_rate=rate)

    async def post(self, *args, **kwargs):
        order_type = 'buy' if 'buy' in self.request.arguments else 'sell'
        price = float(self.get_argument('price', .0))
        count = float(self.get_argument('count', .0))
        current_order = OrderBook(status=1, price_per_item=price, count=count, order_type=order_type)

        orders = await tornado.gen.Task(self.db.get, 'orders')
        if not orders:
            orders = list()
        else:
            orders = json.loads(orders)
        orders.append(current_order.__dict__)
        await tornado.gen.Task(self.db.set, 'orders', json.dumps(orders))

        #self.find_order(current_order)

        self.render("order_book.html", orders=orders)

    async def find_order(self):
        pass
        # искать подходящие заказы с другим типом рекурсивно
        # если заказ с типом продажа:
        #   идем по всем заказам на покупку от самого дорогого
        #   если самый дорогой не подходит, КОНЕЦ
        #   иначе deal() и find_order()
        # если заказ с типом покупка:
        #   идем по всем продажам от самой дешевой
        #   если самая дешевая не подходит, КОНЕЦ
        #   иначе deal() и find_order()

    async def deal(self, buy, sell):
        if buy['count'] == sell['count']:
            buy['status'] = 2  # change status Order -> Deal
            sell['status'] = 2
        elif buy['count'] > sell['count']:
            sell['status'] = 2  # change status Order -> Deal
            # create deal copy
            OrderBook(status=2, price_per_item=sell['price_per_item'],
                      count=sell['count'], order_type='buy')
            buy['count'] -= sell['count']  # calculate the remainder
            buy.update_total_price()
        elif buy['count'] < sell['count']:
            buy['status'] = 2
            OrderBook(status=2, price_per_item=buy['price_per_item'],
                      count=buy['count'], order_type='sell')
            sell['count'] -= buy['count']
            buy.update_total_price()
        await buy, sell,
