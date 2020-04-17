from concurrent.futures import ThreadPoolExecutor
import logging
import os
import random
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(dir_path + '/../logs/dispatch.log')
handler.setFormatter(formatter)
logger = logging.getLogger('dispatch')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


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
        logger.debug("Picking order {}".format(
            order.order_id))
        kitchen.pick_order_from_shelf(order)
