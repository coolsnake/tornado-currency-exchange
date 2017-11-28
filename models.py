from datetime import datetime
import uuid


class OrderBook:
    def __init__(self, status=1, price_per_item=.0, count=.0):
        self.status = status  # 0 - delete, 1 - order, 2 - deal
        self.price_per_item = price_per_item
        self.count = count

        self.total_price = price_per_item * count
        self.date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id = uuid.uuid4().hex

    def __repr__(self):
        fields = vars(self)
        return str(fields)

    def update_total_price(self):
        self.total_price = self.price_per_item * self.count
