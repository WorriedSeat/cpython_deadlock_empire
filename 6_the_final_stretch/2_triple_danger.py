import threading
import time


class EnergyBurst:
    pass


class Queue:
    def __init__(self):
        self._items = []

    @property
    def count(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop(0)


conduit = threading.Lock()
energy_bursts = Queue()
failure_event = threading.Event()

for _ in range(3):
    energy_bursts.enqueue(EnergyBurst())


def FAILURE(msg):
    print(f"[!] FAILURE: {msg}")
    failure_event.set()


def lightning_bolts():
    pass


def fireball():
    pass


def thread_0():
    while not failure_event.is_set():
        with conduit:
            energy_bursts.enqueue(EnergyBurst())
        time.sleep(0)


def thread_1():
    while not failure_event.is_set():
        if energy_bursts.count > 0:
            with conduit:
                energy_bursts.dequeue()
                lightning_bolts()


def thread_2():
    while not failure_event.is_set():
        if energy_bursts.count > 0:
            time.sleep(0)  # race window: T1 drains queue here
            with conduit:
                try:
                    energy_bursts.dequeue()
                except IndexError:
                    FAILURE("T2 dequeued empty queue — TOCTOU between count check and lock")
                else:
                    fireball()


t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t2 = threading.Thread(target=thread_2, name="Thread2", daemon=True)
t0.start()
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("TOCTOU: count > 0 check outside lock allowed T2 to dequeue empty queue.")
else:
    print("Race not triggered in 10 seconds, try again.")
