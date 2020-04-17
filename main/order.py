from datetime import datetime
from enum import Enum


class OrderState(Enum):
    HOT = 1
    COLD = 2
    FROZEN = 3
    OVERFLOW = 4
    WASTED = 5
    PICKED_UP = 6

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
        self._state = None
        self._state_history = []

    def compute_value(self):
        if not self._start_time:
            raise UnboundLocalError("Start time is not set")
        if not self._state:
            raise UnboundLocalError("State is not set")
        order_age = (datetime.now() - self._start_time).seconds
        shelf_decay_modifier = 2 if self._state == OrderState.OVERFLOW else 1
        numerator = float(
            self.shelf_life -
            self.decay_rate * order_age * shelf_decay_modifier)
        return numerator / float(self.shelf_life)

    def set_start_time(self):
        self._start_time = datetime.now()

    def set_state(self, state):
        self._state = state
        self._state_history.append(state)

    def get_start_time(self):
        if not self._start_time:
            raise UnboundLocalError("Start time is not set")
        return self._start_time

    def get_state(self):
        if not self._state:
            raise UnboundLocalError("State is not set")
        return self._state

    def get_order_history_as_string(self):
        return ",".join([val.name for val in self._state_history])
