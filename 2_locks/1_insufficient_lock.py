import threading
import time

# Shared variables
mutex = threading.Lock()
i = 0
failure_event = threading.Event()


def CRITICAL_SECTION():
    time.sleep(0.001)


def FAILURE():
    print(f"[!] FAILURE: i == {i} — lock is insufficient to prevent this state")
    failure_event.set()


def thread_1():
    global i
    while not failure_event.is_set():
        with mutex:
            i = i + 2
            CRITICAL_SECTION()
            if i == 5:
                FAILURE()


def thread_2():
    global i
    while not failure_event.is_set():
        with mutex:
            i = i - 1
            CRITICAL_SECTION()


t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t2 = threading.Thread(target=thread_2, name="Thread2", daemon=True)
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Lock is insufficient — logical failure still reachable.")
else:
    print("Failure not triggered in 10 seconds, try again.")
