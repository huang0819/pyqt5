import logging
import time

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

from utils.weight_reader import WeightReader


class WorkerSignals(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(float)


class WeightReaderWorker(QRunnable):
    def __init__(self, **kwargs):
        super(WeightReaderWorker, self).__init__()

        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.weight_reader = WeightReader(
            dout=self.kwargs['channel_data'],
            pd_sck=self.kwargs['channel_clk'],
            reference_unit=(self.kwargs['reference_unit'])
        )

        self.weight_reader.setup()

        self.stop = False

    @pyqtSlot()
    def run(self):
        try:
            while not self.stop:
                self.weight_reader.read()
                time.sleep(0.1)
        except:
            logging.error("[WEIGHT WORKER] catch an exception.", exc_info=True)
        finally:
            self.signals.finished.emit()  # Done

    def set_stop(self, stop):
        self.stop = stop
