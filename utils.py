import json
import tornado.web
import tornado.gen
from tornado.escape import json_decode
from tornado import httpclient


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
    deals = await get_orders(db, type='deal')
    if not deals:
        deals = list()
    if order_type == 'buy':
        if bool(sell_orders):
            deal_candidate = min(sell_orders, key=lambda x: x['price_per_item'])
            if deal_candidate.get('price_per_item', 0) <= current_order.price_per_item:
                deal_result = await deal(buy=current_order.__dict__, sell=deal_candidate)
                for deal_item in deal_result:
                    deals.append(deal_item)
                await build_order_book(order_type, current_order, db)
            else:
                buy_orders.append(current_order.__dict__)
        else:
            buy_orders.append(current_order.__dict__)

    elif order_type == 'sell':
        if bool(buy_orders):
            deal_candidate = max(buy_orders, key=lambda x: x['price_per_item'])
            if deal_candidate.get('price_per_item', 0) >= current_order.price_per_item:
                deal_result = await deal(buy=current_order.__dict__, sell=deal_candidate)
                for deal_item in deal_result:
                    deals.append(deal_item)
                await build_order_book(order_type, current_order, db)
            else:
                sell_orders.append(current_order.__dict__)
        else:
            sell_orders.append(current_order.__dict__)

    buy_orders.sort(key=lambda x: x['price_per_item'], reverse=True)
    sell_orders.sort(key=lambda x: x['price_per_item'], reverse=True)
    await tornado.gen.Task(db.set, 'buy', json.dumps(buy_orders))
    await tornado.gen.Task(db.set, 'sell', json.dumps(sell_orders))
    await tornado.gen.Task(db.set, 'deal', json.dumps(deals))


async def deal(buy, sell):
    deals = list()
    if buy.get('count', 0) == sell.get('count', 0):
        deal_sell = sell
        deals.append(deal_sell)
        buy['count'] -= sell.get('count', 0)
        sell['count'] -= buy.get('count', 0)
    elif buy.get('count', 0) > sell.get('count', 0):
        deals.append(sell)
        buy['count'] -= sell.get('count', 0)  # calculate the remainder
        buy['total_price'] = buy.get('price_per_item', 0) * buy.get('count', 0)
    elif buy.get('count', 0) < sell.get('count', 0):
        deals.append(buy)
        sell['count'] -= buy.get('count', 0)
        sell['total_price'] = sell.get('price_per_item', 0) * sell.get('count', 0)
    return deals
