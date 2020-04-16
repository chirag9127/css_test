from concurrent.futures import ThreadPoolExecutor
import logging
import random
import time

logging.basicConfig(filename='dispatch.log', level=logging.DEBUG)
logger = logging.getLogger()


"""
Functions for courier related logic
"""


class CourierDispatcher:
    def __init__(self, max_workers=20):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def dispatch(self, order, kitchen):
        """Dispatches courier for order.
        Params: Order
        rtype: None
        """
        self.executor.submit(self.__dispatch, order, kitchen)

    def __dispatch(self, order, kitchen):
        dispatch_time = random.randrange(2, 6)
        logger.debug("Dispatch time for order {} is {}".format(
            order.order_id, dispatch_time))
        time.sleep(dispatch_time)
        kitchen.pick_order_from_shelf(order)
