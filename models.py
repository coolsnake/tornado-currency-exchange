from datetime import datetime
import uuid


class OrderBook:
    def __init__(self, price_per_item=.0, count=.0, status=True):
        self.price_per_item = price_per_item
        self.count = count

        self.total_price = price_per_item * count
        self.date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id = uuid.uuid4().hex
        self.status = status

    def __repr__(self):
        fields = vars(self)
        return str(fields)
