"""
proposed process architecture:
    daemon = True
    2 events:
        self.processing (if currently processing)
        self.free (if currently idling)
"""
from multiprocessing import Process
from multiprocessing import Event as EventP
from threading import Thread
from threading import Event as EventT

class LibProcess(Process):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.daemon = True
        self.processing = EventP()
        self.free = EventP()
        self.processing.clear()
        self.free.set()

class LibThread(Thread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.daemon = True
        self.processing = EventT()
        self.free = EventT()
        self.processing.clear()
        self.free.set()