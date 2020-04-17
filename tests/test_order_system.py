import time

from ..main.order import Order
from ..main.order_system import OrderSystem


def test_upload_orders():
    order_system = OrderSystem()
    order1 = {'id': '1', 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': '2', 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': '3', 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order_system.upload_orders([order1, order2, order3], False)
    assert len(order_system.orders) == 3
    assert order_system.orders[0].order_id == '1'
    assert order_system.orders[-1].order_id == '3'
    assert isinstance(order_system.orders[-1], Order)


def test_processing_rate():
    order_system = OrderSystem()
    order1 = {'id': '1', 'name': 'Ice cream', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order2 = {'id': '2', 'name': 'Peanuts', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order3 = {'id': '3', 'name': 'Rice', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    order4 = {'id': '4', 'name': 'Wheat', 'temp': 'hot',
              'shelfLife': 0.5, 'decayRate': 10}
    start = time.time()
    order_system.upload_orders([order1, order2, order3, order4])
    end = time.time()
    assert 1.9 < (end - start) < 2.1
