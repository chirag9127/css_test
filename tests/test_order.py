from datetime import datetime
import pytest
import time

from ..main.order import Order, OrderState


def test_order():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    assert order.order_id == 1
    assert order.name == 'Test Name'


def test_set_start_time():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    with pytest.raises(UnboundLocalError, match=r"Start time is not set"):
        order.get_start_time()
    order.set_start_time()
    assert (datetime.now() - order.get_start_time()).seconds < 0.1


def test_set_state():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 0.5, 'decayRate': 10})
    with pytest.raises(UnboundLocalError, match=r"State is not set"):
        order.get_state()
    order.set_state(OrderState.OVERFLOW)
    assert order.get_state() == OrderState.OVERFLOW


def test_compute_value_for_overflow():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 2, 'decayRate': 1})
    order.set_start_time()
    order.set_state(OrderState.OVERFLOW)
    assert order.compute_value() > 0.9
    time.sleep(1.0)
    assert -0.001 < order.compute_value() < 0.001


def test_compute_value_for_non_overflow():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 2, 'decayRate': 1})
    order.set_start_time()
    order.set_state(OrderState.HOT)
    assert order.compute_value() > 0.9
    time.sleep(1.0)
    assert 0.499 < order.compute_value() < 0.501
    time.sleep(1.0)
    assert -0.001 < order.compute_value() < 0.001
    time.sleep(1.0)
    assert order.compute_value() < 0


def test_state_history():
    order = Order({'id': 1, 'name': 'Test Name',
                   'temp': 'hot', 'shelfLife': 2, 'decayRate': 1})
    order.set_state(OrderState.HOT)
    order.set_state(OrderState.OVERFLOW)
    order.set_state(OrderState.HOT)
    order.set_state(OrderState.PICKED_UP)
    assert order._state_history == [OrderState.HOT, OrderState.OVERFLOW,
                                    OrderState.HOT, OrderState.PICKED_UP]
