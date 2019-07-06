import numpy as np
import cv2
import time
import requests
import threading
from threading import Thread, Event, ThreadError


class Cam():

    def __init__(self, url):

        self.stream = requests.get(url, stream=True)
        self.thread_cancelled = False
        self.thread = Thread(target=self.run)
        print ("camera initialised")

    def start(self):
        self.thread.start()
        print ("camera stream started")

    def run(self):
        byte_struct = bytes("", 'utf-8')
        while not self.thread_cancelled:
            try:
                byte_struct += self.stream.raw.read(1024)
                a = byte_struct.find('\xff\xd8')
                b = byte_struct.find('\xff\xd9')
                if a != -1 and b != -1:
                    jpg = byte_struct[a:b + 2]

                    byte_struct = byte_struct[b + 2:]
                    img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    cv2.imshow('cam', img)
                    if cv2.waitKey(1) == 27:
                        exit(0)
            except ThreadError:
                self.thread_cancelled = True

    def is_running(self):
        return self.thread.isAlive()

    def shut_down(self):
        self.thread_cancelled = True
        # block while waiting for thread to terminate
        while self.thread.isAlive():
            time.sleep(1)
        return True


if __name__ == "__main__":
    url = 'http://192.168.0.108:8080/?action=stream'
    cam = Cam(url)
    cam.start()