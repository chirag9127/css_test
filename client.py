import json
from order_system import OrderSystem

if __name__ == "__main__":
    order_system = OrderSystem()
    with open('orders.json') as f:
        orders = json.load(f)
        order_system.upload_orders(orders)
