import pytest
from uuid import uuid4
from src.modules.orders.domain.aggregates.order import Order
from src.modules.orders.domain.events.events import OrderCreated

def test_create_order_generates_event():
    customer_id = uuid4()
    total_amount = 100.0
    
    order = Order.create(customer_id, total_amount)
    
    assert order.customer_id == customer_id
    assert order.total_amount == total_amount
    assert order.status == "PENDING"
    
    events = order.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], OrderCreated)
    assert events[0].order_id == order.id
    assert events[0].total_amount == total_amount
