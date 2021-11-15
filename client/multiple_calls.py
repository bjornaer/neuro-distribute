import concurrent.futures
import time

from distribute_challenge import compute_this

out = []


@compute_this
def square(x):
    time.sleep(x)
    return x * x


with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    futures = (executor.submit(square(2).run, True) for _ in range(100))
    time1 = time.time()
    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print(data)
    time2 = time.time()

print(f"Took {time2-time1:.2f} s")
