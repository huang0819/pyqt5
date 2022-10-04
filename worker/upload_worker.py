import sys
import time
import traceback

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

from utils.api import Api


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)

class UploadWorker(QRunnable):
    def __init__(self, base_url, data):
        super(UploadWorker, self).__init__()

        self.signals = WorkerSignals()

        self.api = Api(base_url)

        self.data = data

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            print(self.data)
            time.sleep(3)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done
