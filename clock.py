import threading
import time


class Clock:
    def __init__(self):
        self.clock = 0
        self.clock_thread = threading.Thread(target=self.while_update)
        self.clock_thread.daemon = True
        self.running = False

    def while_update(self):
        while self.running:
            self.clock += 1
            time.sleep(1)

    def increment(self, second):
        self.clock += second

    def start(self):
        if not self.running:
            self.running = True
            self.clock_thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.clock_thread.join()

    def get(self):
        return self.clock
