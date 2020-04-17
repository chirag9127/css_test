import time

from ..main.constants import HOT, COLD, FROZEN, OVERFLOW
from ..main.kitchen import Kitchen
from ..main.order import OrderState
from ..main.order_system import Order


def test_capacities():
    kitchen = Kitchen({HOT: 10, COLD: 10, FROZEN: 10, OVERFLOW: 15})
    assert kitchen.capacities[HOT] == 10
    assert kitchen.capacities[OVERFLOW] == 15
    assert 'hot' in kitchen.shelves
    assert 'cold' in kitchen.shelves
    assert 'overflow' in kitchen.shelves


def test_process_order():
    kitchen = Kitchen({HOT: 1, COLD: 1, FROZEN: 1, OVERFLOW: 3})
    order1 = Order({'id': '1', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order2 = Order({'id': '2', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': '3', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': '4', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order5 = Order({'id': '5', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order6 = Order({'id': '6', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order7 = Order({'id': '7', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    kitchen.process_order(order1)
    kitchen.process_order(order2)
    kitchen.process_order(order3)
    kitchen.process_order(order4)
    kitchen.process_order(order5)
    kitchen.process_order(order6)
    kitchen.process_order(order7)
    assert len(kitchen.shelves[OVERFLOW]) == 3
    assert len(kitchen.shelves[HOT]) == 1
    assert len(kitchen.shelves[FROZEN]) == 0
    assert len(kitchen.shelves[COLD]) == 0


def test_move_from_overflow():
    """
    In this test, we start with a kitchen where there is 1 capacity for
    hot and overflow. Overflow has 1 hot item and cold has no capacity.
    If a new cold item comes in, the hot item should move from overflow
    to hot and the cold item should move to overflow
    """
    kitchen = Kitchen({HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 1})
    order1 = Order({'id': '1', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': '3', 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order1.set_start_time()
    kitchen.shelves[OVERFLOW][order1.order_id] = order1
    kitchen.process_order(order3)
    assert len(kitchen.shelves[HOT]) == 1
    assert len(kitchen.shelves[COLD]) == 0
    assert len(kitchen.shelves[OVERFLOW]) == 1
    assert kitchen.shelves[HOT][order1.order_id] == order1
    assert kitchen.shelves[OVERFLOW][order3.order_id] == order3


def test_cleanup_1():
    """
    Adding two orders to hot and overflow in the beginning.
    They would be wasted by the time we add cold. Here we will test if adding
    to cold deletes the items in hot and over flow.
    """
    kitchen = Kitchen({HOT: 1, COLD: 1, FROZEN: 0, OVERFLOW: 1},
                      run_cleanup=True)
    order1 = Order({'id': '1', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': '3', 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': '4', 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order1.set_start_time()
    order3.set_start_time()
    order1.set_state(HOT)
    order3.set_state(OVERFLOW)
    kitchen.shelves[OVERFLOW][order3.order_id] = order3
    kitchen.shelves[HOT][order1.order_id] = order1
    time.sleep(1)
    kitchen.process_order(order4)
    assert len(kitchen.shelves[HOT]) == 0
    assert len(kitchen.shelves[COLD]) == 1
    assert len(kitchen.shelves[OVERFLOW]) == 0
    assert len(kitchen.wasted) == 2


def test_cleanup_2():
    """
    More test cases for testing the cleanup feature
    """
    kitchen = Kitchen({HOT: 2, COLD: 1, FROZEN: 0, OVERFLOW: 1},
                      run_cleanup=True)
    order1 = Order({'id': '1', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    # item with longer shelf life. Not to be deleted
    order2 = Order({'id': '2', 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 10, 'decayRate': 10})
    order3 = Order({'id': '3', 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': '4', 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order1.set_start_time()
    order2.set_start_time()
    order3.set_start_time()
    order1.set_state(OrderState.HOT)
    order2.set_state(OrderState.HOT)
    order3.set_state(OrderState.OVERFLOW)
    kitchen.shelves[OVERFLOW][order3.order_id] = order3
    kitchen.shelves[HOT][order1.order_id] = order1
    kitchen.shelves[HOT][order2.order_id] = order2
    time.sleep(1)
    kitchen.process_order(order4)
    assert len(kitchen.shelves[HOT]) == 1
    assert len(kitchen.shelves[COLD]) == 1
    assert len(kitchen.shelves[OVERFLOW]) == 0
    assert len(kitchen.wasted) == 2
    assert '2' in kitchen.shelves[HOT]
