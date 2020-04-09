import logging
import pickle
import random
import threading
import time

from kitchen import main_kitchen

logging.basicConfig(filename='dispatch.log', level=logging.DEBUG)
logger = logging.getLogger()


"""
Functions for courier related logic
"""


def dispatch(order):
    """Dispatches courier for order.
    Params: Order
    rtype: None
    """
    dispatch_thread = threading.Thread(target=_dispatch, args=(order,))
    dispatch_thread.start()


def _dispatch(order):
    dispatch_time = random.randrange(2, 6)
    logger.debug("Dispatch time for order {} is {}".format(
        order.order_id, dispatch_time))
    time.sleep(dispatch_time)
    _pick_order(order)


def _pick_order(order):
    main_kitchen.lock.acquire()
    try:
        shelves = main_kitchen.shelves
        for pos, order_to_pick in enumerate(shelves[order.temp]):
            if order.order_id == order_to_pick.order_id:
                logger.debug("Picking up order {} from {}".format(
                    order.order_id, order.temp))
                del shelves[order.temp][pos]
                return
        for pos, order_to_pick in enumerate(shelves['overflow']):
            if order.order_id == order_to_pick.order_id:
                logger.debug("Picking up order {} from overflow".format(
                    order.order_id))
                del shelves['overflow'][pos]
                return
        logger.debug("Could not pickup order {}".format(
            order.order_id))
    finally:
        main_kitchen.lock.release()
