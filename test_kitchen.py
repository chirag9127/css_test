from kitchen import Kitchen
from order_system import Order


def test_kitchen():
    kitchen = Kitchen({})
    assert kitchen.capacity == 10
    assert 'hot' in kitchen.shelves
    assert 'cold' in kitchen.shelves
    assert 'overflow' in kitchen.shelves


def test_variable_capacity():
    kitchen = Kitchen({'hot': 10, 'cold': 10, 'frozen': 25, 'overflow': 15})
    assert kitchen.capacity == 10
    assert 'hot' in kitchen.shelves
    assert 'cold' in kitchen.shelves
    assert 'overflow' in kitchen.shelves
    assert kitchen.capacities['frozen'] == 25


def test_capacity_usage():
    kitchen = Kitchen({'hot': 1, 'cold': 1, 'frozen': 1, 'overflow': 3})
    order1 = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order2 = Order({'id': 2, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order3 = Order({'id': 3, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order4 = Order({'id': 4, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order5 = Order({'id': 5, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order6 = Order({'id': 6, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    order7 = Order({'id': 7, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    kitchen.update_shelf(order1)
    kitchen.update_shelf(order2)
    kitchen.update_shelf(order3)
    kitchen.update_shelf(order4)
    kitchen.update_shelf(order5)
    kitchen.update_shelf(order6)
    kitchen.update_shelf(order7)
    assert len(kitchen.shelves['overflow']) == 3
    assert len(kitchen.shelves['hot']) == 1
    assert len(kitchen.shelves['frozen']) == 0
    assert len(kitchen.shelves['cold']) == 0
