import threading
import time

# Shared variables
sync = threading.Event()                # stays signaled until explicitly cleared
counter = 0
failure_event = threading.Event()


def FAILURE():
    print(f"[!] FAILURE: counter = {counter} (odd!) — Thread1 read counter mid-increment")
    failure_event.set()


def thread_1():
    while not failure_event.is_set():
        sync.wait()
        time.sleep(0)
        if counter % 2 == 1:
            FAILURE()


def thread_2():
    global counter
    while not failure_event.is_set():
        sync.clear()
        counter += 1
        time.sleep(0)
        counter += 1
        sync.set()


t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t2 = threading.Thread(target=thread_2, name="Thread2", daemon=True)
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("ManualResetEvent does NOT protect Thread1 from seeing counter mid-increment.")
else:
    print("Race not triggered in 10 seconds, try again.")
