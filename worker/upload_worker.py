import logging

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

from utils.api import Api


class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(int)

class UploadWorker(QRunnable):
    def __init__(self, base_url, data):
        super(UploadWorker, self).__init__()

        self.signals = WorkerSignals()

        self.api = Api(base_url)

        self.data = data

    @pyqtSlot()
    def run(self):
        try:
            status_code = self.api.upload_data(self.data)
            self.signals.result.emit(1 if status_code == 200 else 0)
        except:
            logging.error("[UPLOAD WORKER] catch an exception.", exc_info=True)
        finally:
            logging.info(f"[UPLOAD WORKER] finish upload {self.data['file_name']}")
            self.signals.finished.emit()  # Done
