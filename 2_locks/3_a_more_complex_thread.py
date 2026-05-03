import threading
import time

# Shared variables
mutex  = threading.RLock()          # Allows take the lock multiple times by the same thread
mutex2 = threading.RLock()
mutex3 = threading.Lock()

flag = False
deadlock_event = threading.Event()


def CRITICAL_SECTION():
    time.sleep(0.001)


def thread_1():
    global flag
    while not deadlock_event.is_set():
        time.sleep(0)
        if mutex.acquire(blocking=False):
            time.sleep(0)
            mutex3.acquire()
            mutex.acquire()
            CRITICAL_SECTION()
            mutex.release()
            time.sleep(0)
            mutex2.acquire()
            flag = False
            mutex2.release()
            mutex3.release()
        else:
            mutex2.acquire()
            flag = True
            mutex2.release()


def thread_2():
    global flag
    while not deadlock_event.is_set():
        if flag:
            mutex2.acquire()
            time.sleep(0)
            mutex.acquire()
            flag = False
            CRITICAL_SECTION()
            mutex.release()
            time.sleep(0)
            mutex2.acquire()    # mutex2 leaked at count=2, no Exit ever called
        else:
            mutex.acquire()
            flag = False
            time.sleep(0)
            mutex.release()


t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t2 = threading.Thread(target=thread_2, name="Thread2", daemon=True)
t1.start()
t2.start()

t1.join(timeout=5)
t2.join(timeout=5)

if t1.is_alive() or t2.is_alive():
    print("[!] DEADLOCK: Thread1 holds mutex + mutex3, waiting for mutex2")
    print("              Thread2 holds mutex2 (leaked), waiting for mutex")
else:
    print("No deadlock this run, try again.")
