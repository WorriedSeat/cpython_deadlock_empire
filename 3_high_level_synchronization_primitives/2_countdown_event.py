import threading
import time


class CountdownEvent:
    """
    CountdownEvent(N): Signal() decrements the counter,
    Wait() blocks until counter reaches 0.
    """
    def __init__(self, initial_count):
        self._count = initial_count
        self._lock  = threading.Lock()
        self._done  = threading.Event()
        if initial_count <= 0:
            self._done.set()

    def signal(self):
        with self._lock:
            self._count -= 1
            if self._count <= 0:
                self._done.set()

    def wait(self, timeout=None):
        return self._done.wait(timeout=timeout)


def run_once():
    progress = [0]
    event = CountdownEvent(3)

    both_loaded = threading.Barrier(2)

    def thread_1():
        temp = progress[0]
        both_loaded.wait()
        time.sleep(0)
        progress[0] = temp + 20

        time.sleep(0)
        if progress[0] >= 20:
            event.signal()

        event.wait(timeout=1)

    def thread_2():
        temp = progress[0]
        both_loaded.wait()
        progress[0] = temp + 30

        time.sleep(0)
        if progress[0] >= 30:
            event.signal()

        temp = progress[0]
        time.sleep(0)
        progress[0] = temp + 50

        time.sleep(0)
        if progress[0] >= 80:
            event.signal()

        event.wait(timeout=1)

    t1 = threading.Thread(target=thread_1, daemon=True)
    t2 = threading.Thread(target=thread_2, daemon=True)
    t1.start()
    t2.start()
    t1.join(timeout=2)
    t2.join(timeout=2)

    signals_fired = 3 - event._count
    deadlocked = signals_fired < 3
    return deadlocked, progress[0], signals_fired


for attempt in range(1, 101):
    deadlocked, final_progress, signals = run_once()
    if deadlocked:
        print(
            f"[!] DEADLOCK on attempt {attempt}: "
            f"only {signals} of 3 signals fired, progress={final_progress}"
        )
        print("CountdownEvent does NOT protect against races on shared variables.")
        break
else:
    print("Deadlock not triggered in 100 attempts.")
