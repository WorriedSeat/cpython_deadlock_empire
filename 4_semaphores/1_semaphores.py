import threading
import time

semaphore = threading.Semaphore(0)
_in_cs = [0]
failure_event = threading.Event()


def FAILURE():
    print(f"[!] RACE: _in_cs={_in_cs[0]} — both threads in critical section at once")
    print("SemaphoreSlim(0): Thread1 releases on timeout, leaking the counter.")
    failure_event.set()


def critical_section():
    _in_cs[0] += 1
    if _in_cs[0] > 1:
        FAILURE()
    time.sleep(0.005)
    _in_cs[0] -= 1


def thread_0():
    while not failure_event.is_set():
        semaphore.acquire()
        critical_section()
        semaphore.release()


def thread_1():
    while not failure_event.is_set():
        if semaphore.acquire(blocking=False):
            critical_section()
            semaphore.release()
        else:
            semaphore.release()
            time.sleep(0)

t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t0.start()
t1.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Semaphore(0) + leaked Release() on timeout = CS not protected.")
else:
    print("Race not triggered in 10 seconds, try again.")
