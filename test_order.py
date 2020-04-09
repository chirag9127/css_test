from order_system import Order


def test_order():
    order = Order({'id': 1, 'name': 'Test Name', 'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    assert order.order_id == 1
    assert order.name == 'Test Name'
