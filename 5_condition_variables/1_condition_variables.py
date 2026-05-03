import threading
import time

condition = threading.Condition()
queue = []
failure_event = threading.Event()


def FAILURE():
    print("[!] FAILURE: dequeue on empty queue — both consumers woke on a single item")
    print("Bug: 'if' instead of 'while' before condition.wait() — no re-check after wakeup.")
    failure_event.set()


def consumer():
    while not failure_event.is_set():
        with condition:
            if len(queue) == 0:
                condition.wait()
            if failure_event.is_set():
                return
            try:
                queue.pop(0)
            except IndexError:
                FAILURE()


def producer():
    while not failure_event.is_set():
        with condition:
            queue.append(42)
            condition.notify_all()
        time.sleep(0)


t0 = threading.Thread(target=consumer, name="Thread0", daemon=True)
t1 = threading.Thread(target=consumer, name="Thread1", daemon=True)
t2 = threading.Thread(target=producer, name="Thread2", daemon=True)
t0.start()
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Condition variable: 'if' instead of 'while' allows both consumers to dequeue.")
else:
    print("Race not triggered in 10 seconds, try again.")
