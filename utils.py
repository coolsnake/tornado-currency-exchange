import json
import tornado.web
import tornado.gen
from tornado.escape import json_decode
from tornado import httpclient

from models import OrderBook


async def get_orders(db, type=None):
    orders = await tornado.gen.Task(db.get, type)
    if not orders:
        orders = list()
    else:
        orders = json.loads(orders)
    return orders


async def get_rate(db):
    rate = await tornado.gen.Task(db.get, 'rate')
    if not rate:
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
        await tornado.gen.Task(db.set, 'rate', rate, 60)
    return rate


async def build_order_book(order_type, current_order, db):
    buy_orders = await get_orders(db, type='buy')
    sell_orders = await get_orders(db, type='sell')
    if order_type == 'buy':
        buy_orders.append(current_order.__dict__)
    elif order_type == 'sell':
        sell_orders.append(current_order.__dict__)
    # искать подходящие заказы с другим типом рекурсивно
    # если заказ с типом покупка:
    #   идем по всем продажам от самой дешевой
    #   если самая дешевая не подходит, КОНЕЦ
    #   иначе deal() и find_order()
    # если заказ с типом продажа:
    #   идем по всем заказам на покупку от самого дорогого
    #   если самый дорогой не подходит, КОНЕЦ
    #   иначе deal() и find_order()
    buy_orders.sort(key=lambda x: x['price_per_item'], reverse=True)
    sell_orders.sort(key=lambda x: x['price_per_item'], reverse=True)
    await tornado.gen.Task(db.set, 'buy', json.dumps(buy_orders))
    await tornado.gen.Task(db.set, 'sell', json.dumps(sell_orders))


async def deal(buy, sell):
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
