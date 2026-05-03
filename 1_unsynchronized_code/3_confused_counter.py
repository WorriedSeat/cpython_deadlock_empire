import threading
import time


def FAILURE(first, second):
    print(
        f"[!] FAILURE: second={second} but first={first} "
        f"— expected first=2, got first={first} (lost update on first++)"
    )


def business_logic():
    time.sleep(0)


def run_once():
    first = 0
    second = 0
    failed = False

    def thread_1():
        nonlocal first, second, failed
        business_logic()
        temp = first            # first++ expanded — non-atomic
        time.sleep(0)           # context switch can happen here
        first = temp + 1
        second += 1
        if second == 2 and first != 2:
            failed = True

    def thread_2():
        nonlocal first, second
        business_logic()
        temp = first            # first++ expanded — non-atomic
        time.sleep(0)           # context switch can happen here
        first = temp + 1
        second += 1

    t1 = threading.Thread(target=thread_1, name="Thread1")
    t2 = threading.Thread(target=thread_2, name="Thread2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return failed, first, second


for attempt in range(1000):
    failed, first, second = run_once()
    if failed:
        FAILURE(first, second)
        print(f"Race triggered on attempt {attempt + 1}")
        break
else:
    print("Race not triggered in 1000 attempts")
