import threading
import time

# Shared variables
flag = False
_in_cs = 0
failure_event = threading.Event()


def CRITICAL_SECTION():
    global _in_cs
    _in_cs += 1
    if _in_cs > 1:
        print(
            f"[!] RACE CONDITION: {threading.current_thread().name} "
            f"entered critical section while another thread is already inside!"
        )
        failure_event.set()
    time.sleep(0.001)
    _in_cs -= 1


def thread_first_army():
    global flag
    while not failure_event.is_set():
        while flag:          # spin-wait: while (flag == true) {}
            time.sleep(0)
        time.sleep(0)        # context switch can happen here
        flag = True
        CRITICAL_SECTION()
        flag = False


def thread_second_army():
    global flag
    while not failure_event.is_set():
        while flag:          # spin-wait: while (flag == true) {}
            time.sleep(0)
        time.sleep(0)        # context switch can happen here
        flag = True
        CRITICAL_SECTION()
        flag = False


t1 = threading.Thread(target=thread_first_army, name="FirstArmy", daemon=True)
t2 = threading.Thread(target=thread_second_army, name="SecondArmy", daemon=True)
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Flag-based 'lock' is NOT safe — race condition confirmed.")
else:
    print("Race condition not triggered in 10 seconds, try again.")
