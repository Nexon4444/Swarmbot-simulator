import threading
import time
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

e = threading.Event()
def func():
    for i in range(0, 100):
        e.wait()
        print("1")
        e.clear()

def allow():
    for i in range(0, 100):
        e.set()
        time.sleep(1)

t1 = threading.Thread(target=func)
t2 = threading.Thread(target=allow)

t1.start()
t2.start()

t1.join()
t2.join()