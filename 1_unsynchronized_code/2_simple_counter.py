import threading
import time

# Shared variables
counter = 0
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


def thread_five_headed():
    global counter
    while not failure_event.is_set():
        temp = counter
        time.sleep(0)           # context switch can happen here
        counter = temp + 1
        if counter == 5:
            CRITICAL_SECTION()


def thread_three_headed():
    global counter
    while not failure_event.is_set():
        temp = counter
        time.sleep(0)           # context switch can happen here
        counter = temp + 1
        if counter == 3:
            CRITICAL_SECTION()


t1 = threading.Thread(target=thread_five_headed, name="FiveHeaded", daemon=True)
t2 = threading.Thread(target=thread_three_headed, name="ThreeHeaded", daemon=True)
t1.start()
t2.start()

failure_event.wait(timeout=10)
if failure_event.is_set():
    print("Counter-based logic is NOT safe — race condition confirmed.")
else:
    print("Race condition not triggered in 10 seconds, try again.")
