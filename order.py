"""
Class for representing order object.
Converts json to object.
"""


class Order:
    def __init__(self, order):
        self.order_id = order['id']
        self.name = order['name']
        self.temp = order['temp']
        self.shelf_life = order['shelfLife']
        self.decay_rate = order['decayRate']
