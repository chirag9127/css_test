from datetime import datetime

from constants import OVERFLOW

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
        self._start_time = None
        self._shelf = None

    def compute_value(self):
        if not self._start_time:
            raise UnboundLocalError("Start time is not set")
        if not self._shelf:
            raise UnboundLocalError("Shelf is not set")
        order_age = (datetime.now() - self._start_time).seconds
        shelf_decay_modifier = 2 if self._shelf == OVERFLOW else 1
        numerator = float(
            self.shelf_life -
            self.decay_rate * order_age * shelf_decay_modifier)
        return numerator / float(self.shelf_life)

    def set_start_time(self):
        self._start_time = datetime.now()

    def set_shelf(self, shelf):
        self._shelf = shelf

    def get_start_time(self):
        if not self._start_time:
            raise UnboundLocalError("Start time is not set")
        return self._start_time

    def get_shelf(self):
        if not self._shelf:
            raise UnboundLocalError("Shelf is not set")
        return self._shelf
