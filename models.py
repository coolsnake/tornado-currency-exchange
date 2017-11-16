import datetime


class OrderBook:
    def __init__(self, status=0, price_per_item=.0, count=.0, order_type='sell'):
        self.status = status  # 0 - delete, 1 - order, 2 - deal
        self.price_per_item = price_per_item
        self.count = count
        self.order_type = order_type

        self.total_price = price_per_item * count
        self.date_time = datetime.now()

    def __repr__(self):
        fields = vars(self)
        return str(fields)
