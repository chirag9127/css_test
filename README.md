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
