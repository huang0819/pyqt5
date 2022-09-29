import sys
import traceback
import numpy as np

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from utils.depth_camera import DepthCamera


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    data
        int indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    data = pyqtSignal(np.ndarray)

class DepthCameraWorker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, **kwargs):
        super(DepthCameraWorker, self).__init__()

        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.depth_camera = DepthCamera('record')

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            while True:
                image, depth = self.depth_camera.read()
                if image is not None:
                    rgb_image = np.copy(image[:, :, ::-1])
                    self.signals.data.emit(rgb_image)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done
