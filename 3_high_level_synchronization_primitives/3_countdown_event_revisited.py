import threading
import time


class CountdownEvent:
    """
    Auto-resetting CountdownEvent: when wait() passes, it resets
    count back to initial — creating a race window for the next cycle.
    """
    def __init__(self, initial_count):
        self._initial = initial_count
        self._count = initial_count
        self._lock = threading.Lock()
        self._done = threading.Event()
        if initial_count <= 0:
            self._done.set()

    def signal(self):
        with self._lock:
            self._count -= 1
            if self._count <= 0:
                self._done.set()

    def wait(self, timeout=None):
        result = self._done.wait(timeout=timeout)
        if result:
            with self._lock:
                self._count = self._initial
                self._done.clear()
        return result


def run_once():
    progress = [0]
    event = CountdownEvent(3)
    outcome = [None]

    def thread_0():
        while outcome[0] is None:
            temp = progress[0]
            time.sleep(0)
            progress[0] = temp + 20

            event.signal()
            time.sleep(0)

            if not event.wait(timeout=1):
                outcome[0] = 'deadlock'
                return
            if progress[0] == 100:
                outcome[0] = 'game_over'
                return

    def thread_1():
        while outcome[0] is None:
            temp = progress[0]
            time.sleep(0)
            progress[0] = temp + 30

            event.signal()

            temp = progress[0]
            time.sleep(0)
            progress[0] = temp + 50

            event.signal()
            time.sleep(0)

            if not event.wait(timeout=1):
                outcome[0] = 'deadlock'
                return
            if progress[0] == 100:
                outcome[0] = 'game_over'
                return

    t0 = threading.Thread(target=thread_0, daemon=True)
    t1 = threading.Thread(target=thread_1, daemon=True)
    t0.start()
    t1.start()
    t0.join(timeout=3)
    t1.join(timeout=3)

    if outcome[0] is None:
        outcome[0] = 'timeout'
    return outcome[0], progress[0]


for attempt in range(1, 101):
    result, final_progress = run_once()
    if result == 'deadlock':
        print(
            f"[!] DEADLOCK on attempt {attempt}: "
            f"a thread missed the CountdownEvent reset and blocked forever. "
            f"progress={final_progress}"
        )
        print("Auto-resetting CountdownEvent introduces a race between wait() and the next cycle.")
        break
else:
    print("Deadlock not triggered in 100 attempts.")
