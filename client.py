import argparse
import json
from main.order_system import OrderSystem

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_workers', type=int, default=20,
                        help='maximum number of dispatchers')
    parser.add_argument('--order_rate', type=float, default=2,
                        help='order rate for the kitchen')
    parser.add_argument('--capacities', type=json.loads,
                        default='{"hot": 10, "cold": 10,'
                                '"frozen": 10, "overflow": 15}',
                        help='capacities for each shelf')
    parser.add_argument('--results_file', type=str, default='results.tsv',
                        help='file for output')
    args = parser.parse_args()
    order_system = OrderSystem(order_rate=args.order_rate,
                               max_workers=args.max_workers,
                               capacities=args.capacities,
                               results_file=args.results_file)
    with open('orders.json') as f:
        orders = json.load(f)
        order_system.upload_orders(orders)
