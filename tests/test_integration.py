from datetime import datetime
import threading
import time

from ..main.constants import HOT, COLD, OVERFLOW, FROZEN
from ..main.order import OrderState
from ..main.order_system import OrderSystem


def test_3_orders():
    """
    Place 3 orders. Based on our logic, we take ~1.5 s to place 3 orders.
    The pickups can happen anytime between 2 nd 7.5 seconds. We sleep
    on the main thread for 8 s and then see what's left on the shelves
    """
    order_system = OrderSystem(max_workers=3, run_cleanup=False)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4  # 3 workers + main thread
    assert len(order_system.kitchen.shelves[HOT]) == 3
    time.sleep(8)
    assert threading.active_count() == 4  # 3 workers + main thread
    assert len(order_system.kitchen.shelves[HOT]) == 0


def test_no_overflow():
    """
    In this test case, we test no overflow and 1 shelf for hot items
    The expectation is that two items will be wasted.
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 0},
        max_workers=3, run_cleanup=False)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 40, 'decayRate': 1}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4  # 3 workers + main thread
    assert len(order_system.kitchen.shelves[HOT]) == 1
    assert len(order_system.kitchen.wasted) == 2
    time.sleep(8)
    assert threading.active_count() == 4  # 3 workers + main thread
    assert len(order_system.kitchen.shelves[HOT]) == 0
    assert len(order_system.kitchen.wasted) == 2


def test_overflow():
    """
    In this test case, we have 2 overflow spot and expect 0 wastage
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 2},
        max_workers=3, run_cleanup=False)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 40, 'decayRate': 2}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 40, 'decayRate': 2}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 40, 'decayRate': 2}
    order_system.upload_orders([order1, order2, order3])
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 1
    assert len(order_system.kitchen.wasted) == 0
    assert len(order_system.kitchen.shelves[OVERFLOW]) == 2
    time.sleep(8)
    assert threading.active_count() == 4
    assert len(order_system.kitchen.shelves[HOT]) == 0
    assert len(order_system.kitchen.wasted) == 0
    assert len(order_system.kitchen.shelves[OVERFLOW]) == 0


def test_max_workers():
    """
    In this test case, we verify the number of workers spawned
    """
    order_system = OrderSystem(
        capacities={HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 2},
        max_workers=10, run_cleanup=False)
    orders = []
    for i in range(100):
        orders.append({'id': i, 'name': 'Ice cream', 'temp': 'hot',
                       'shelfLife': 0.5, 'decayRate': 10})
    order_system.upload_orders(orders)
    assert threading.active_count() <= 11  # atmost 10 workers + 1 main thread
    time.sleep(8)
    assert threading.active_count() <= 11  # atmost 10 workers + 1 main thread
    time.sleep(8)
    assert threading.active_count() <= 11  # atmost 10 workers + 1 main thread


def test_e2e_flow_with_cleanup():
    order_system = OrderSystem(
        capacities={HOT: 2, COLD: 0, FROZEN: 0, OVERFLOW: 3},
        max_workers=10, run_cleanup=True)
    order1 = {'id': 1, 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.001, 'decayRate': 100}
    order2 = {'id': 2, 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 10, 'decayRate': 1}
    order3 = {'id': 3, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 50, 'decayRate': 1}
    order4 = {'id': 4, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 50, 'decayRate': 1}
    order5 = {'id': 5, 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 50, 'decayRate': 1}
    time_start = datetime.now()
    order_system.upload_orders([order1, order2, order3, order4, order5])
    time_upload_orders = datetime.now()
    assert (time_upload_orders - time_start).seconds == 2
    assert len(order_system.kitchen.shelves[HOT]) <= 2
    assert len(order_system.kitchen.wasted) == 1
    assert len(order_system.kitchen.shelves[OVERFLOW]) == 2
    time.sleep(10)
    assert len(order_system.kitchen.wasted) == 1
    assert len(order_system.kitchen.picked_up) == 4
    assert order_system.kitchen.wasted[0]._state_history == [OrderState.HOT, OrderState.WASTED]
