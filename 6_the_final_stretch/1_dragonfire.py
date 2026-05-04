import threading
import time

firebreathing = threading.Lock()
fireball = threading.Semaphore(0)
c = [0]
_in_cs = [0]
failure_event = threading.Event()


def FAILURE():
    print(f"[!] FAILURE: both threads in critical_section simultaneously (c={c[0]})")
    failure_event.set()


def critical_section():
    _in_cs[0] += 1
    if _in_cs[0] > 1:
        FAILURE()
    time.sleep(0.005)
    _in_cs[0] -= 1


def incinerate_enemies():
    pass


def blast_enemies():
    time.sleep(0)


def thread_0():
    while not failure_event.is_set():
        with firebreathing:
            incinerate_enemies()
            if fireball.acquire(blocking=False):
                blast_enemies()
                if fireball.acquire(blocking=False):
                    if fireball.acquire(blocking=False):
                        critical_section()
            temp = c[0]
            time.sleep(0)
            c[0] = temp - 1
            temp = c[0]
            time.sleep(0)
            c[0] = temp + 1


def thread_1():
    while not failure_event.is_set():
        if c[0] < 2:
            fireball.release()
            temp = c[0]
            time.sleep(0)
            c[0] = temp + 1
        else:
            critical_section()


t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t0.start()
t1.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Race: non-atomic c let T1 over-release fireball; both threads entered critical_section.")
else:
    print("Race not triggered in 10 seconds, try again.")
