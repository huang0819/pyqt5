import logging
import numpy as np

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from utils.depth_camera import DepthCamera


class WorkerSignals(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(np.ndarray)

class DepthCameraWorker(QRunnable):
    def __init__(self, **kwargs):
        super(DepthCameraWorker, self).__init__()

        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.depth_camera = DepthCamera()

        self.stop = False

    @pyqtSlot()
    def run(self):
        try:
            while not self.stop:
                image, depth = self.depth_camera.read()
                if image is not None:
                    rgb_image = np.copy(image[:, :, ::-1])
                    self.signals.data.emit(rgb_image)
        except:
            logging.error("[DEPTH CAMERA WORKER] catch an exception.", exc_info=True)
        finally:
            self.signals.finished.emit()

    def set_stop(self, stop):
        self.stop = stop
