import threading
import time


class Dragon:
    pass


class NonThreadSafeQueue:
    """
    Queue whose Enqueue/Dequeue each have a 3-step structure:
      1. enter inconsistent state
      2. gain / lose an element
      3. return to consistent state
    A GIL switch between steps 1 and 2 exposes the inconsistency.
    """
    def __init__(self):
        self._items = []
        self._count = 0

    def enqueue(self, item):
        self._count += 1
        time.sleep(0)
        self._items.append(item)
        # step 3: consistent

    def dequeue(self):
        self._count -= 1
        time.sleep(0)
        return self._items.pop(0)
        # step 3: consistent


semaphore = threading.Semaphore(0)
queue = NonThreadSafeQueue()
failure_event = threading.Event()


def FAILURE(msg):
    print(f"[!] FAILURE: {msg}")
    print("Non-thread-safe queue: dequeue ran while enqueue was incomplete.")
    failure_event.set()


def thread_0():
    while not failure_event.is_set():
        if semaphore.acquire(timeout=0.5):
            try:
                queue.dequeue()
            except IndexError:
                FAILURE("dequeue on empty queue — Thread1 signaled before enqueuing")


def thread_1():
    while not failure_event.is_set():
        semaphore.release()
        time.sleep(0)
        queue.enqueue(Dragon())


t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t0.start()
t1.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Semaphore signaled before enqueue — consumer dequeues empty queue.")
else:
    print("Race not triggered in 10 seconds, try again.")
