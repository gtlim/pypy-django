import requests

host = 'http://0.0.0.0:8000/'
endpoint = 'ormperf'
import time
for k in range(300):
    t0 = time.time()
    for k in range(100):
        r = requests.get(host + endpoint, timeout=10)

    print(time.time() - t0)
