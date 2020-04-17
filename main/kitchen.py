from collections import defaultdict
from datetime import datetime
import logging
import os
import sys
import threading

from .constants import OVERFLOW, SHELF_TO_STATE, STATE_TO_SHELF
from .order import OrderState

dir_path = os.path.dirname(os.path.realpath(__file__))
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(dir_path + '/../logs/kitchen.log')
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
    def __init__(self, capacities, run_cleanup=False,
                 results_file='results.tsv'):
        self.lock = threading.Lock()
        self.shelves = defaultdict(dict)
        self.capacities = capacities
        for shelf_type in self.capacities:
            self.shelves[shelf_type]
        self.wasted = []  # this is primarily for book keeping
        self.picked_up = []
        self.run_cleanup = run_cleanup
        self.results_file = results_file

    def process_order(self, order):
        """Processes each order. Called by order system
        Params: Order
        rtype: None
        """
        order.set_start_time()
        self.__put_order_on_shelf(order)

    def pick_order_from_shelf(self, order):
        """
        Function for courier to pick up order from kitchen
        Params: Order
        rtype: None
        """
        self.lock.acquire()
        try:
            if self.__check_order_is_wasted(order):
                return

            self.__pickup_order(order)
        finally:
            self.__update_results(order)
            self.lock.release()

    def __update_results(self, order):
        try:
            with open(self.results_file, 'a+') as f:
                f.write("\t".join([order.order_id,
                                   order.get_start_time().strftime(
                                       "%d-%b-%Y (%H:%M:%S.%f)"),
                                   datetime.now().strftime(
                                       "%d-%b-%Y (%H:%M:%S.%f)"),
                                   str(order.compute_value()),
                                   order.get_order_history_as_string(),
                                   "\n"]))
        except Exception as e:
            logger.debug("Logging error {}".format(e))

    def __update_shelf_and_order(self, order, shelf):
        self.shelves[shelf][order.order_id] = order
        order.set_state(SHELF_TO_STATE[shelf])
        logger.debug("putting order {} on shelf {} with value {}".format(
            order.order_id, shelf, order.compute_value()))

    def __move_to_wasted(self, order):
        self.wasted.append(order)
        order.set_state(OrderState.WASTED)
        logger.debug("Order {} is wasted with value {}".format(
            order.order_id, order.compute_value()))

    def __move_from_overflow(self, order):
        """If order cannot be placed in nomal shelf, this function will try to
        clear overflow and move it there
        Time complexity: O(C)
        Params: Order
        rtype: Boolean
        """
        for o_id, order_to_move in self.shelves[OVERFLOW].items():
            if len(self.shelves[order_to_move.temp]) \
                    < self.capacities[order_to_move.temp]:
                self.__update_shelf_and_order(order_to_move, order_to_move.temp)
                del self.shelves[OVERFLOW][o_id]
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
        """
        Representation of kitchen shelves
        """
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
                    self.__move_to_wasted(order)
                    logger.debug("Order wasted {}".format(
                        order.order_id))
            else:
                self.__update_shelf_and_order(order, order.temp)
                logger.debug("Order added {} to {} and has value {}".format(
                    order.order_id, order.temp, order.compute_value()))
            logger.debug("Current status of shelves: {}".format(self))
        finally:
            self.lock.release()

    def __check_order_is_wasted(self, order):
        """
        Function to check order is wasted
        Params: Order
        rtype: Bool
        """
        if order.get_state() == OrderState.WASTED:
            logger.debug("Could not pickup order {} with value {} "
                         "because it is wasted".format(
                             order.order_id, order.compute_value()))
            return True
        if order.compute_value() < 0:
            logger.debug("Could not pickup order {} with value {}".format(
                order.order_id, order.compute_value()))
            del self.shelves[STATE_TO_SHELF[order.get_state()]][order.order_id]
            self.__move_to_wasted(order)
            return True
        return False

    def __pickup_order(self, order):
        """
        Function for changing state of order during pickup
        """
        logger.debug("Picking up order {} from {}".format(
            order.order_id, order.get_state()))
        self.picked_up.append(order)
        del self.shelves[STATE_TO_SHELF[order.get_state()]][order.order_id]
        order.set_state(OrderState.PICKED_UP)

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
        wastage. We also do 2 since its a cheap check.
        """
        items_to_delete = []
        logger.debug("Starting cleanup")
        for shelf, orders in self.shelves.items():
            for o_id, order in orders.items():
                if order.compute_value() < 0:
                    items_to_delete.append((shelf, o_id))
                    logger.debug("Marking order {} with "
                                 "value {} for cleanup".format(
                                     order.order_id, order.compute_value()))
        logger.debug("Items to be deleted {}".format(items_to_delete))
        for item in items_to_delete:
            logger.debug("Cleaning order {} from shelf {}".format(
                item[1], item[0]))
            self.__move_to_wasted(self.shelves[item[0]][item[1]])
            del self.shelves[item[0]][item[1]]
        logger.debug("Finishing cleanup")
