import threading
import time


class Golem:
    pass


class NonThreadSafeQueue:
    def __init__(self):
        self._items = []
        self._count = 0

    @property
    def count(self):
        return self._count

    def enqueue(self, item):
        self._count += 1
        time.sleep(0)
        self._items.append(item)

    def dequeue(self):
        self._count -= 1
        return self._items.pop(0)


queue = NonThreadSafeQueue()
failure_event = threading.Event()


def FAILURE(msg):
    print(f"[!] FAILURE: {msg}")
    print("TOCTOU race: count > 0 was True but items was empty when dequeue ran.")
    failure_event.set()


def thread_0():
    while not failure_event.is_set():
        queue.enqueue(Golem())


def thread_1():
    while not failure_event.is_set():
        if queue.count > 0:
            try:
                queue.dequeue()
            except IndexError:
                FAILURE(f"dequeue on empty queue (count={queue.count})")


t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t0.start()
t1.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Non-thread-safe queue: Count check does not protect against internal inconsistency.")
else:
    print("Race not triggered in 10 seconds, try again.")
