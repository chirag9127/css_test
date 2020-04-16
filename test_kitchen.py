import time

from constants import HOT, COLD, FROZEN, OVERFLOW, WASTED
from kitchen import Kitchen
from order_system import Order


def test_capacities():
    kitchen = Kitchen({HOT: 10, COLD: 10, FROZEN: 10, OVERFLOW: 15})
    assert kitchen.capacities[HOT] == 10
    assert kitchen.capacities[OVERFLOW] == 15
    assert 'hot' in kitchen.shelves
    assert 'cold' in kitchen.shelves
    assert 'overflow' in kitchen.shelves


def test_process_order():
    kitchen = Kitchen({HOT: 1, COLD: 1, FROZEN: 1, OVERFLOW: 3})
    order1 = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order2 = Order({'id': 2, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': 3, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': 4, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order5 = Order({'id': 5, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order6 = Order({'id': 6, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order7 = Order({'id': 7, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    kitchen.process_order(order1)
    kitchen.process_order(order2)
    kitchen.process_order(order3)
    kitchen.process_order(order4)
    kitchen.process_order(order5)
    kitchen.process_order(order6)
    kitchen.process_order(order7)
    assert len(kitchen.shelves['overflow']) == 3
    assert len(kitchen.shelves['hot']) == 1
    assert len(kitchen.shelves['frozen']) == 0
    assert len(kitchen.shelves['cold']) == 0


def test_move_from_overflow():
    """
    In this test, we start with a kitchen where there is 1 capacity for
    hot and overflow. Overflow has 1 hot item and cold has no capacity.
    If a new cold item comes in, the hot item should move from overflow
    to hot and the cold item should move to overflow
    """
    kitchen = Kitchen({HOT: 1, COLD: 0, FROZEN: 0, OVERFLOW: 1})
    order1 = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': 3, 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    kitchen.shelves[OVERFLOW].append(order1)
    kitchen.process_order(order3)
    assert len(kitchen.shelves[HOT]) == 1
    assert len(kitchen.shelves[COLD]) == 0
    assert len(kitchen.shelves[OVERFLOW]) == 1
    assert kitchen.shelves[HOT][0].order_id == 1
    assert kitchen.shelves[OVERFLOW][0].order_id == 3


def test_cleanup_1():
    """
    Adding two orders to hot and overflow in the beginning.
    They would be wasted by the time we add cold. Here we will test if adding
    to cold deletes the items in hot and over flow.
    """
    kitchen = Kitchen({HOT: 1, COLD: 1, FROZEN: 0, OVERFLOW: 1},
                      run_cleanup=True)
    order1 = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': 3, 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': 4, 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order1.set_start_time()
    order3.set_start_time()
    order1.set_shelf(HOT)
    order3.set_shelf(OVERFLOW)
    kitchen.shelves[OVERFLOW].append(order3)
    kitchen.shelves[HOT].append(order1)
    time.sleep(1)
    kitchen.process_order(order4)
    assert len(kitchen.shelves[HOT]) == 0
    assert len(kitchen.shelves[COLD]) == 1
    assert len(kitchen.shelves[OVERFLOW]) == 0
    assert len(kitchen.shelves[WASTED]) == 2


def test_cleanup_2():
    """
    More test cases for testing the cleanup feature
    """
    kitchen = Kitchen({HOT: 2, COLD: 1, FROZEN: 0, OVERFLOW: 1},
                      run_cleanup=True)
    order1 = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 0.5, 'decayRate': 10})
    # item with longer shelf life. Not to be deleted
    order2 = Order({'id': 2, 'name': 'Test Name', 'temp': 'hot',
                    'shelfLife': 10, 'decayRate': 10})
    order3 = Order({'id': 3, 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': 4, 'name': 'test name', 'temp': 'cold',
                    'shelfLife': 0.5, 'decayRate': 10})
    order1.set_start_time()
    order2.set_start_time()
    order3.set_start_time()
    order1.set_shelf(HOT)
    order2.set_shelf(HOT)
    order3.set_shelf(OVERFLOW)
    kitchen.shelves[OVERFLOW].append(order3)
    kitchen.shelves[HOT].append(order1)
    kitchen.shelves[HOT].append(order2)
    time.sleep(1)
    kitchen.process_order(order4)
    assert len(kitchen.shelves[HOT]) == 1
    assert len(kitchen.shelves[COLD]) == 1
    assert len(kitchen.shelves[OVERFLOW]) == 0
    assert len(kitchen.shelves[WASTED]) == 2
    assert kitchen.shelves[HOT][0].order_id == 2
