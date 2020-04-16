from collections import defaultdict
import logging
import threading

from constants import OVERFLOW, WASTED


logging.basicConfig(filename='kitchen.log', level=logging.DEBUG)
logger = logging.getLogger()


"""
Class for kitchen including the shelves. We are using a lock for all writes
to the shelf
"""


class Kitchen:
    def __init__(self, capacities):
        self.lock = threading.Lock()
        self.shelves = defaultdict(list)
        self.capacities = capacities
        for shelf_type in self.capacities:
            self.shelves[shelf_type]
        self.shelves[WASTED]  # this is primarily for book keeping

    def process_order(self, order):
        """Processes each order. Called by order system
        Params: Order
        rtype: None
        """
        print ("Processing order: {}".format(order.order_id))
        self.__put_order_on_shelf(order)

    def __move_from_overflow(self, order):
        """If order cannot be placed in nomal shelf, this function will try to
        clear overflow and move it there
        Time complexity: O(C + C) = O(C)
        Params: Order
        rtype: Boolean
        """
        for pos, order_to_move in enumerate(self.shelves[OVERFLOW]):
            if len(self.shelves[order_to_move.temp]) \
                    < self.capacities[order_to_move.temp]:
                self.shelves[order_to_move.temp].append(order_to_move)
                del self.shelves[OVERFLOW][pos]
                return True
        return False

    def __add_to_overflow(self, order):
        """
        Add to overflow if default shelf space is not available
        Params: Order
        rtype: Boolean
        """
        if len(self.shelves[OVERFLOW]) >= self.capacities[OVERFLOW]:
            if not self.__move_from_overflow(order):
                return False
        self.shelves[OVERFLOW].append(order)
        return True

    def __str__(self):
        return ", ".join(
            ["{}::{}".format(
                shelf_name, len(shelf))
                for (shelf_name, shelf) in self.shelves.items()])

    def __put_order_on_shelf(self, order):
        """
        Update shelf. We are using a lock for this since the state of the
        order can be changed by both the kitchen and the courier threads
        Params: Order
        rtype: None
        """
        self.lock.acquire()
        try:
            if len(self.shelves[order.temp]) >= self.capacities[order.temp]:
                can_add_to_overflow = self.__add_to_overflow(order)
                if not can_add_to_overflow:
                    self.shelves[WASTED].append(order)
                    logger.debug("ORDER WASTED!!! {}".format(
                        order.order_id))
                    print ("ORDER WASTED!!! {}".format(order.order_id))
            else:
                print ("Order added {} to {}".format(
                    order.order_id, order.temp))
                logger.debug("Order added {} to {}".format(
                    order.order_id, order.temp))
                self.shelves[order.temp].append(order)
            print("Current status of shelves: {}".format(self))
            logger.debug("Current status of shelves: {}".format(self))
        finally:
            self.lock.release()

    def pick_order_from_shelf(self, order):
        self.lock.acquire()
        try:
            shelves = self.shelves
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
            self.lock.release()
