# CSS take home test

1. To setup the environment `conda env create -f environment.yml`
2. Run `source activate chirag_css_programming`
3. To run the program `python client.py`
4. To run tests `pytest`

## Key changes

1. Added unit tests and e2e tests
2. Added logic for cleaning up orders if order value is below 0 (more details below)
3. Cleaned up logs. Routed kitchen logs to both console and kitchen.log (more details below)
4. Cleaned up folder structure
5. Added argparser so that the client can tune configs (more details below)
6. Added logic to create a results folder (more details below)
7. Created thread pool for dispatchers instead of instantiating new threads for every order
8. Change data structure of shelves from dict(list) to dict(dict). This makes delete O(1) instead of O(k) where k is size of shelf

## Conventions followed

1. Class structure: constructor followed by public methods followed by private methods
2. Import order: First import external modules and then import application modules (in alphabetical order by first non python word. i.e. not from, import)

## Cleanup after an order has reached end of life
Cleanup helps clean space and reduce wastage. However, there is a cost to when the cleanup should be. There are many ways to do this:
1. Cleanup all orders before putting an order. This cleanup is of the order of O(n) where n is the number of orders.
2. Check if order has reached below 0 value and then deciding on whether to pick up or not. This is constant time operation and very simple to implement. However, since the cleanup is later, there might be some wastage.
3. The other option will be to do cleanup for only the potential temp shelf to be added and the overflow shelf. This can still lead to some wastage in the edge case where wasted order in other shelves can create space for something to move from overflow to that shelf. And the overall time does not improve significantly (unless one of the shelves is significantly smaller).
4. The final option will be to have a background process deleting wasted orders like in a garbage collector. This will need a lot of tuning to get right for a given usecase.

We are going to be implementing option 1 since that will minimize wastage. We also do 2 since its a cheap check.

## Logs
We create two log files here: kitchen.log and dispatch.log.
### Kitchen logs
```
2020-04-17 08:30:47,212 - kitchen - DEBUG - Starting cleanup
2020-04-17 08:30:47,212 - kitchen - DEBUG - Items to be deleted []
2020-04-17 08:30:47,212 - kitchen - DEBUG - Finishing cleanup
2020-04-17 08:30:47,212 - kitchen - DEBUG - putting order a8cfcb76-7f24-4420-a5ba-d46dd77bdffd on shelf frozen with value 1.0
2020-04-17 08:30:47,212 - kitchen - DEBUG - Order added a8cfcb76-7f24-4420-a5ba-d46dd77bdffd to frozen and has value 1.0
2020-04-17 08:30:47,212 - kitchen - DEBUG - Current status of shelves: hot::0, cold::0, frozen::1, overflow::0
2020-04-17 08:30:47,718 - kitchen - DEBUG - Starting cleanup
2020-04-17 08:30:47,718 - kitchen - DEBUG - Items to be deleted []
2020-04-17 08:30:47,718 - kitchen - DEBUG - Finishing cleanup
2020-04-17 08:30:47,718 - kitchen - DEBUG - putting order 58e9b5fe-3fde-4a27-8e98-682e58a4a65d on shelf frozen with value 1.0
2020-04-17 08:30:47,718 - kitchen - DEBUG - Order added 58e9b5fe-3fde-4a27-8e98-682e58a4a65d to frozen and has value 1.0
2020-04-17 08:30:47,719 - kitchen - DEBUG - Current status of shelves: hot::0, cold::0, frozen::2, overflow::0
```
### Dispatch logs
```
2020-04-17 08:30:47,213 - dispatch - DEBUG - Dispatch time for order a8cfcb76-7f24-4420-a5ba-d46dd77bdffd is 5
2020-04-17 08:30:47,719 - dispatch - DEBUG - Dispatch time for order 58e9b5fe-3fde-4a27-8e98-682e58a4a65d is 2
2020-04-17 08:30:48,223 - dispatch - DEBUG - Dispatch time for order 2ec069e3-576f-48eb-869f-74a540ef840c is 5
2020-04-17 08:30:48,730 - dispatch - DEBUG - Dispatch time for order 690b85f7-8c7d-4337-bd02-04e04454c826 is 3
2020-04-17 08:30:49,233 - dispatch - DEBUG - Dispatch time for order 972aa5b8-5d83-4d5e-8cf3-8a1a1437b18a is 5
2020-04-17 08:30:49,720 - dispatch - DEBUG - Picking order 58e9b5fe-3fde-4a27-8e98-682e58a4a65d
```

## Usage

```
usage: client.py [-h] [--max_workers MAX_WORKERS] [--order_rate ORDER_RATE]
                 [--capacities CAPACITIES] [--results_file RESULTS_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --max_workers MAX_WORKERS
                        maximum number of dispatchers
  --order_rate ORDER_RATE
                        order rate for the kitchen
  --capacities CAPACITIES
                        capacities for each shelf
  --results_file RESULTS_FILE
                        file for output
```

## Results

We are storing the results in results.tsv which is of the format: order_id, creation_time, pickup_time, value, order_state_history
```

a8cfcb76-7f24-4420-a5ba-d46dd77bdffd	17-Apr-2020 (06:35:40.212806)	17-Apr-2020 (06:35:44.219322)	0.874	FROZEN,PICKED_UP	
2ec069e3-576f-48eb-869f-74a540ef840c	17-Apr-2020 (06:35:41.222624)	17-Apr-2020 (06:35:44.231169)	0.9963855421686747	COLD,PICKED_UP	
c18e1242-0856-4203-a98c-7066ead3bd6b	17-Apr-2020 (06:35:42.736982)	17-Apr-2020 (06:35:44.743051)	0.9985873605947956	COLD,PICKED_UP
```
