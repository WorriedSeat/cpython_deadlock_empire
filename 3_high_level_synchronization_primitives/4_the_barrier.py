import threading
import time


def run_once():
    fireballCharge = [0]
    barrier = threading.Barrier(2)
    failure = [False]
    charge_at_failure = [None]

    def thread_0():
        while not failure[0]:
            fireballCharge[0] += 1
            try:
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                return
            time.sleep(0)           # race window
            charge = fireballCharge[0]
            if charge < 2:
                failure[0] = True
                charge_at_failure[0] = charge
                barrier.abort()
                return

    def thread_1():
        while not failure[0]:
            fireballCharge[0] += 1
            try:
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                return

    def thread_2():
        while not failure[0]:
            fireballCharge[0] += 1
            try:
                barrier.wait(timeout=2)
                if failure[0]:
                    return
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                return
            fireballCharge[0] = 0

    t0 = threading.Thread(target=thread_0, daemon=True)
    t1 = threading.Thread(target=thread_1, daemon=True)
    t2 = threading.Thread(target=thread_2, daemon=True)
    t0.start()
    t1.start()
    t2.start()
    t0.join(timeout=5)
    t1.join(timeout=5)
    t2.join(timeout=5)

    return failure[0], charge_at_failure[0]


for attempt in range(1, 101):
    triggered, charge = run_once()
    if triggered:
        print(
            f"[!] ASSERT FAILED on attempt {attempt}: "
            f"fireballCharge={charge} < 2"
        )
        print("Barrier(2) with 3 threads: Thread2 reset the charge before Thread0 checked it.")
        break
else:
    print("Failure not triggered in 100 attempts.")
