import threading
import time

# Shared variables
mutex  = threading.Lock()
mutex2 = threading.Lock()


def CRITICAL_SECTION():
    time.sleep(0.001)


def thread_1():
    mutex.acquire()
    time.sleep(0)       # context switch can happen here
    mutex2.acquire()    # waits forever if Thread2 already holds mutex2
    CRITICAL_SECTION()
    mutex.release()
    mutex2.release()


def thread_2():
    mutex2.acquire()
    time.sleep(0)       # context switch can happen here
    mutex.acquire()     # waits forever if Thread1 already holds mutex
    CRITICAL_SECTION()
    mutex2.release()
    mutex.release()


t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t2 = threading.Thread(target=thread_2, name="Thread2", daemon=True)
t1.start()
t2.start()

t1.join(timeout=3)
t2.join(timeout=3)

if t1.is_alive() or t2.is_alive():
    print("[!] DEADLOCK: threads are stuck waiting for each other forever")
else:
    print("No deadlock this run — one thread grabbed both locks first, try again.")
