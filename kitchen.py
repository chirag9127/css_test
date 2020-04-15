from collections import defaultdict
import threading

from constants import HOT, COLD, FROZEN, OVERFLOW


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

    def process_order(self, order):
        """Processes each order. Called by order system
        Params: Order
        rtype: None
        """
        print ("Processing order: {}".format(order.order_id))
        self.__update_shelf(order)

    def __move_from_overflow(self, order):
        """If order cannot be placed in nomal shelf, this function will try to
        clear overflow and move it there
        Time complexity: O(C + C) = O(C)
        Params: Order
        rtype: Boolean
        """
        for pos, order_to_move in enumerate(self.shelves[OVERFLOW]):
            if len(self.shelves[order.temp]) < self.capacities[order.temp]:
                self.shelves[order.temp].append(order_to_move)
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
        self.shelves['overflow'].append(order)
        return True

    def __update_shelf(self, order):
        """
        Update shelf
        Params: Order
        rtype: None
        """
        self.lock.acquire()
        try:
            if len(self.shelves[order.temp]) >= self.capacities[order.temp]:
                can_add_to_overflow = self.__add_to_overflow(order)
                if not can_add_to_overflow:
                    print ("ORDER WASTED!!! {}".format(order.order_id))
            else:
                print ("Order added {} to {}".format(order.order_id, order.temp))
                self.shelves[order.temp].append(order)
            print("Current status of shelves {}".format(self.shelves))
        finally:
            self.lock.release()


main_kitchen = Kitchen({HOT: 10, COLD: 10, FROZEN: 10, OVERFLOW: 15})
