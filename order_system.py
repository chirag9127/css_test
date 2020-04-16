from collections import deque
import time

from constants import HOT, COLD, FROZEN, OVERFLOW
from courier_dispatcher import CourierDispatcher
from order import Order
from kitchen import Kitchen


"""
Class for representing order system.
Processes orders and calls the kitchen object and
dispatcher.
"""


class OrderSystem:
    def __init__(self, order_rate=2,
                 capacities={HOT: 10, COLD: 10, FROZEN: 10, OVERFLOW: 15},
                 max_workers=20, run_cleanup=True):
        self.order_rate = order_rate  # rate of sending of orders
        self.orders = deque()
        self.time_to_wait = 1.0 / float(order_rate)
        self.kitchen = Kitchen(capacities, run_cleanup=run_cleanup)
        self.courier_dispatcher = CourierDispatcher(max_workers)

    def __send_to_kitchen(self):
        """
        contains the rate limiting logic to send orders
        to the kitchen
        How to make this not spiky?
        - After each order, you wait for 1 / order rate time
        - Ideally we would keep a sliding window of time stamps
        """
        while self.orders:
            curr_order = self.orders.popleft()
            self.kitchen.process_order(curr_order)
            self.courier_dispatcher.dispatch(curr_order, self.kitchen)
            time.sleep(self.time_to_wait)

    def upload_orders(self, orders, send_to_kitchen=True):
        """
        param send_to_kitchen is for testing
        """
        for order in orders:
            self.orders.append(Order(order))
        if send_to_kitchen:
            self.__send_to_kitchen()
