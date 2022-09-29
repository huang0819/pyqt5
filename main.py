import sys
import traceback
import os

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout, QLabel
import time

from ui.user_button import UserButton
from ui.main_page import Ui_MainWindow
from ui.user_select import UserSelect
from ui.user_control import UserControl

from worker.camera_worker import DepthCameraWorker

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

        self.viewData = QLabel('test')
        self.viewData.setMinimumSize(640, 480)
        self.main_window.verticalLayout.addWidget(self.viewData)

        # 多執行序
        self.thread_pool = QThreadPool()
        self.depth_camera_worker = DepthCameraWorker()
        self.depth_camera_worker.signals.data.connect(self.show_image)

        self.thread_pool.start(self.depth_camera_worker)

        self.frame_num = 0

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

    def show_image(self, img):
        len_y, len_x, _ = img.shape  # 取得影像尺寸

        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)

        # 建立 Qimage 物件 (RGB格式)
        qimg = QImage(img.data, len_x, len_y, QImage.Format_RGB888)

        self.viewData.setPixmap(QPixmap.fromImage(qimg))

        # Frame Rate
        if self.frame_num == 0:
            self.time_start = time.time()
        if self.frame_num >= 0:
            self.frame_num += 1
            self.t_total = time.time() - self.time_start
            if self.frame_num % 100 == 0:
                self.frame_rate = float(self.frame_num) / self.t_total
                print(self.frame_rate)

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
