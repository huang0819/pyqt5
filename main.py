import sys
import traceback
import os

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout
import time

from ui.user_button import UserButton
from ui.main_page import Ui_MainWindow
from ui.user_select import UserSelect
from ui.user_control import UserControl

from utils.depth_camera import DepthCamera

from fake_data.user_data import USER_DATA


class UI_PAGE_NAME:
    USER_SELECT = 0
    USER_CONTROL = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.showFullScreen()

        self.user_select = UserSelect()
        self.user_control = UserControl()

        self.qls = QStackedLayout()
        self.qls.addWidget(self.user_select)
        self.qls.addWidget(self.user_control)

        self.main_window.verticalLayout.addLayout(self.qls)

        self.main_window.title.setText('XX國小X年X班')

        self.user_buttons = []
        for (index, user_data) in enumerate(USER_DATA):
            self.user_buttons.append(UserButton(data=user_data, index=index))
            self.user_buttons[index].resize(self.user_buttons[index].sizeHint())
            self.user_select.gridLayout.addWidget(self.user_buttons[index], index // 5, index % 5, 1, 1)
            self.user_buttons[index].user_click_signal.connect(self.user_button_click_handler)

        # 感測器
        self.depth_camera = DepthCamera('record', debug=True)

        # 多執行序
        self.thread_pool = QThreadPool()

        worker1 = Worker(self.depth_camera.run)
        worker2 = Worker(lambda: self.count(1))
        worker2.signals.finished.connect(self.test)

        self.thread_pool.start(worker1)
        self.thread_pool.start(worker2)

    def test(self):
        print('test')

    def save_file(self):
        file_name = 'test'
        file_path = os.path.join('record', '{}.npz'.format(file_name))
        self.depth_camera.save_file(file_path)

    def count(self, delay):
        for i in range(5):
            print(i)
            time.sleep(delay)

    def user_button_click_handler(self, data):
        print(data)
        self.main_window.title.setText(f"您好，{data['name']}同學")

        self.qls.setCurrentIndex(UI_PAGE_NAME.USER_CONTROL)


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

    progress
        int indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    data = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
