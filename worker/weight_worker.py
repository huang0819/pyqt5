import sys
import traceback

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from utils.weight_reader import WeightReader


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    data
        float value of weight

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    data = pyqtSignal(float)

class WeightReaderWorker(QRunnable):
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
        super(WeightReaderWorker, self).__init__()

        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.weight_reader = WeightReader(
            dout=self.kwargs['channel_data'],
            pd_sck=self.kwargs['channel_clk'],
            reference_unit=(self.kwargs['reference_unit'])
        )

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            while True:
                self.weight_reader.read()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done
