from collections import deque
import time

from courier_dispatcher import dispatch
from kitchen import main_kitchen


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
        # self.shelf_id = 'hot'


"""
Class for representing order system.
Processes orders and calls the kitchen object and
dispatcher.
"""


class OrderSystem:
    def __init__(self, order_rate=2):
        self.order_rate = order_rate  # rate of sending of orders
        self.orders = deque()

    def send_to_kitchen(self):
        """
        contains the rate limiting logic to send orders
        to the kitchen
        How to make this not spiky?
        - After each order, you wait for 1 / order rate time
        - Ideally we would keep a sliding window of time stamps
        """
        counter = 0
        while self.orders:
            curr_order = self.orders.popleft()
            counter += 1
            main_kitchen.process_order(curr_order)
            dispatch(curr_order)
            if counter % self.order_rate == 0:
                time.sleep(1)

    def upload_order(self, order):
        self.orders.append(Order(order))
