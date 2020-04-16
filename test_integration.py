import threading
import time

from constants import HOT, COLD, FROZEN, OVERFLOW, WASTED
from order_system import OrderSystem


def test_3_orders():
    """
    Place 3 orders. Based on our logic, we take ~1.5 s to place 3 orders.
    The pickups can happen anytime between 2 nd 7.5 seconds. We sleep
    on the main thread for 8 s and then see what's left on the shelves
    """
    order_system = OrderSystem(max_workers=3)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 3
    time.sleep(8)
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 0


def test_no_overflow():
    """
    In this test case, we test no overflow and 1 shelf for hot items
    The expectation is that two items will be wasted.
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 0},
        max_workers=3)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 1
    assert len(order_system.kitchen.shelves[WASTED]) == 2
    time.sleep(8)
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 0
    assert len(order_system.kitchen.shelves[WASTED]) == 2


def test_overflow():
    """
    In this test case, we have 2 overflow spot and expect 0 wastage
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 2},
        max_workers=3)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 1
    assert len(order_system.kitchen.shelves[WASTED]) == 0
    assert len(order_system.kitchen.shelves[OVERFLOW]) == 2
    time.sleep(8)
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 0
    assert len(order_system.kitchen.shelves[WASTED]) == 0
    assert len(order_system.kitchen.shelves[OVERFLOW]) == 0


def test_max_workers():
    """
    In this test case, we verify the number of workers spawned
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 2},
        max_workers=10)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1] * 100)
    assert threading.active_count() <= 11
    time.sleep(8)
    assert threading.active_count() <= 11
    time.sleep(8)
    assert threading.active_count() <= 11
