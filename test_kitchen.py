from constants import HOT, COLD, FROZEN, OVERFLOW
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
