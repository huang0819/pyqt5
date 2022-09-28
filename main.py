import sys
import traceback
import os

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QStackedLayout, QPushButton
from data_collect import Ui_MainWindow
import time

from ui.user_button import UserButton

from utils.depth_camera import DepthCamera


class Panel(QWidget):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()

        background_color = {'background-color': f"{kwargs['background_color']};"}

        style = f"QWidget{background_color}".replace("'", '')

        self.setStyleSheet(style)

        onePanel_layout = QHBoxLayout()
        qlabel = QLabel(kwargs['label'])
        qlabel.setStyleSheet("color: blue; font-weight: bold; font-size: 24px")
        onePanel_layout.addWidget(qlabel)

        self.setLayout(onePanel_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()

        one = Panel(label='test 1', background_color='#66CCFF')
        two = Panel(label='test 2', background_color='#66FFCC')
        three = Panel(label='test 3', background_color='#EE0000')

        qls = QStackedLayout()
        qls.addWidget(one)
        qls.addWidget(two)
        qls.addWidget(three)

        self.ui.verticalLayout.addLayout(qls)

        # self.ui.pushButton.clicked.connect(self.test)

        self.userBtn = UserButton(label='王曉明', style=0)
        self.userBtn.resize(self.userBtn.sizeHint())
        self.ui.gridLayout_2.addWidget(self.userBtn, 4, 0, 1, 1)

        self.userBtn2 = UserButton(label='陳曉華', style=1)
        self.userBtn2.resize(self.userBtn2.sizeHint())
        self.ui.gridLayout_2.addWidget(self.userBtn2, 4, 1, 1, 1)

        self.userBtn3 = UserButton(label='林大偉', style=0)
        self.userBtn3.resize(self.userBtn3.sizeHint())
        self.ui.gridLayout_2.addWidget(self.userBtn3, 4, 2, 1, 1)

        self.userBtn4 = UserButton(label='菜比八', style=1)
        self.userBtn4.resize(self.userBtn4.sizeHint())
        self.ui.gridLayout_2.addWidget(self.userBtn4, 4, 3, 1, 1)

        # self.userBtn.button.clicked.connect(lambda: print('hi'))

        self.ui.pushButton.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton, qls))
        self.ui.pushButton_2.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton_2, qls))
        self.ui.pushButton_3.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton_3, qls))

        # 感測器
        self.depth_camera = DepthCamera('record', debug=True)

        # 多執行序
        self.thread_pool = QThreadPool()

        worker1 = Worker(self.depth_camera.run)
        worker2 = Worker(lambda: self.count(2))

        self.thread_pool.start(worker1)
        self.thread_pool.start(worker2)

    def save_file(self):
        file_name = 'test'
        file_path = os.path.join('record', '{}.npz'.format(file_name))
        self.depth_camera.save_file(file_path)

    def count(self, delay):
        i = 0
        while (True):
            print(i)
            i += 1
            time.sleep(delay)

    def buttonIsClicked(self, button, qls):
        print(button.text())
        dic = {
            "1": 0,
            "2": 1,
            "3": 2
        }
        index = dic[button.text()]
        qls.setCurrentIndex(index)


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
