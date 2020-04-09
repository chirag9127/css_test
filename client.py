import json
from order_system import OrderSystem

if __name__ == "__main__":
    order_system = OrderSystem(2)
    with open('orders.json') as f:
        orders = json.load(f)
        for order in orders:
            order_system.upload_order(order)
    order_system.send_to_kitchen()
