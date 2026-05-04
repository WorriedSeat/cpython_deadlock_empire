import threading
import time

darkness = [0]
evil = [0]
fortress = threading.Semaphore(0)
sanctum = threading.Condition()
_in_cs = [0]
failure_event = threading.Event()


def FAILURE():
    print(f"[!] FAILURE: both threads in critical_section simultaneously")
    failure_event.set()


def critical_section():
    _in_cs[0] += 1
    if _in_cs[0] > 1:
        FAILURE()
    time.sleep(0.005)
    _in_cs[0] -= 1


def thread_0():
    while not failure_event.is_set():
        temp_d = darkness[0]
        time.sleep(0)
        darkness[0] = temp_d + 1
        temp_e = evil[0]
        evil[0] = temp_e + 1
        if darkness[0] != 2 and evil[0] != 2:
            if fortress.acquire(blocking=False):
                if fortress.acquire(blocking=False):
                    with sanctum:
                        notified = sanctum.wait(timeout=2)
                    if notified:
                        critical_section()
                else:
                    fortress.release()


def thread_1():
    while not failure_event.is_set():
        temp_d = darkness[0]
        time.sleep(0)
        darkness[0] = temp_d + 1
        temp_e = evil[0]
        time.sleep(0)
        evil[0] = temp_e + 1
        if darkness[0] != 2 and evil[0] == 2:
            with sanctum:
                sanctum.notify()
            critical_section()
        fortress.release()
        darkness[0] = 0
        evil[0] = 0


t0 = threading.Thread(target=thread_0, name="Thread0", daemon=True)
t1 = threading.Thread(target=thread_1, name="Thread1", daemon=True)
t0.start()
t1.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Race: darkness lost-update + evil TOCTOU + Monitor.Wait/Pulse put both threads in critical_section.")
else:
    print("Race not triggered in 10 seconds, try again.")
