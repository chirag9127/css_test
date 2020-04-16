from collections import defaultdict
import logging
import sys
import threading

from constants import OVERFLOW, WASTED

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('kitchen.log')
handler.setFormatter(formatter)
handler1 = logging.StreamHandler(sys.stdout)
handler1.setFormatter(formatter)
logger = logging.getLogger('kitchen')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(handler1)


"""
Class for kitchen including the shelves. We are using a lock for all writes
to the shelf
"""


class Kitchen:
    def __init__(self, capacities, run_cleanup=False):
        self.lock = threading.Lock()
        self.shelves = defaultdict(list)
        self.capacities = capacities
        for shelf_type in self.capacities:
            self.shelves[shelf_type]
        self.shelves[WASTED]  # this is primarily for book keeping
        self.run_cleanup = run_cleanup

    def process_order(self, order):
        """Processes each order. Called by order system
        Params: Order
        rtype: None
        """
        order.set_start_time()
        self.__put_order_on_shelf(order)

    def __update_shelf_and_order(self, order, shelf):
        self.shelves[shelf].append(order)
        order.set_shelf(shelf)

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
                self.__update_shelf_and_order(order_to_move, order_to_move.temp)
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
        self.__update_shelf_and_order(order, OVERFLOW)
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
            if self.run_cleanup:
                self.__cleanup()
            if len(self.shelves[order.temp]) >= self.capacities[order.temp]:
                can_add_to_overflow = self.__add_to_overflow(order)
                if not can_add_to_overflow:
                    self.__update_shelf_and_order(order, WASTED)
                    logger.debug("ORDER WASTED!!! {}".format(
                        order.order_id))
            else:
                self.__update_shelf_and_order(order, order.temp)
                logger.debug("Order added {} to {} and has value {}".format(
                    order.order_id, order.temp, order.compute_value()))
            logger.debug("Current status of shelves: {}".format(self))
        finally:
            self.lock.release()

    def pick_order_from_shelf(self, order):
        self.lock.acquire()
        try:
            shelves = self.shelves
            if order.get_shelf() == WASTED:
                logger.debug("Could not pickup order {} with value {}" \
                             "because it is wasted".format(
                                 order.order_id, order.compute_value()))
                return
            if order.compute_value() < 0:
                self.__update_shelf_and_order(order, WASTED)
                for pos, order_to_delete in enumerate(self.shelves[order.get_shelf()]):
                    if order_to_delete.order_id == order.order_id:
                        del self.shelves[order.get_shelf][pos]

            for pos, order_to_pick in enumerate(shelves[order.get_shelf()]):
                if order.order_id == order_to_pick.order_id:
                    logger.debug("Picking up order {} from {}".format(
                        order.order_id, order.get_shelf()))
                    del shelves[order.get_shelf()][pos]
                    return
            logger.debug("Could not pickup order {} with value {}".format(
                order.order_id, order.compute_value()))
        finally:
            self.lock.release()

    def __cleanup(self):
        """
        Function to cleanup based on order value. Cleanup helps clean space and
        reduce wastage. However, there is a cost to when the cleanup should be.
        There are many ways to do this.
        1. Cleanup all orders before putting an order. This cleanup is of the
        order of O(n) where n is the number of orders.
        2. Check if order has reached below 0 value and then deciding on whether
        to pick up or not. This is constant time operation and very simple to
        implement. However, since the cleanup is later, there might be
        some wastage.
        3. The other option will be to do cleanup for only the potential temp
        shelf to be added and the overflow shelf. This can still lead to some
        wastage in the edge case where wasted order in other shelves can create
        space for something to move from overflow to that shelf.
        4. The final option will be to have a background process deleting wasted
        orders like in a garbage collector. This will need a lot of tuning to
        get right for a given usecase.
        We are going to be implementing option 1 since that will minimize
        wastage.
        """
        for shelf, orders in self.shelves.items():
            if shelf == WASTED:
                continue
            for pos, order in enumerate(orders):
                if order.compute_value() < 0:
                    logger.debug("deleting order {} with value {}".format(
                        order.order_id, order.compute_value()))
                    self.__update_shelf_and_order(order, WASTED)
                    del orders[pos]
