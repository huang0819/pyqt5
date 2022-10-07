import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QLabel

import logging
import cv2
import numpy as np

from utils.depth_camera import DepthCamera


class COMPONENT_NAME:
    BLANK = 0
    DEPTH_CAMERA = 1
    LED = 2
    WEIGHT = 3


class Button(QPushButton):
    FONT = QtGui.QFont('微軟正黑體', 36)

    GREEN = {
        'common_color': '#548235',
        'pressed_color': '#A9D18E'
    }
    BLUE = {
        'common_color': '#2E75B6',
        'pressed_color': '#9DC3E6'
    }
    RED = {
        'common_color': '#d73131',
        'pressed_color': '#e26c6c'
    }

    BTN_STYLE = """
        QPushButton {{
            background-color: {common_color};
            color: #FFFFFF;
            border-style: outset;
            padding: 2px;
            font: 58px 微軟正黑體;
            border-width: 1px;
            border-radius: 10px;
            border-color: transparent;
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}"""

    def __init__(self, parent, text, start, size):
        super(Button, self).__init__()

        self.setParent(parent)
        self.setFont(self.FONT)
        self.setText(text)
        self.setStyleSheet(self.BTN_STYLE.format(**self.BLUE))
        self.resize(*size)
        self.setGeometry(QtCore.QRect(*start, self.width(), self.height()))


class TestModulePage(QWidget):
    led_signal = pyqtSignal(str)
    LED_STATUS = ['state_setup', 'state_idle', 'state_busy']

    def __init__(self, **kwargs):
        super(TestModulePage, self).__init__()
        self.kwargs = kwargs

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 1040)

        self.btn_depth_camera = Button(self, '深度攝影機', (0, 0), (500, 200))
        self.btn_depth_camera.clicked.connect(lambda: self.change_component(COMPONENT_NAME.DEPTH_CAMERA))
        self.btn_led = Button(self, 'LED模組', (0, 300), (500, 200))
        self.btn_led.clicked.connect(lambda: self.change_component(COMPONENT_NAME.LED))
        self.btn_weight = Button(self, '重量感測器', (0, 600), (500, 200))

        self.component_area = QWidget(self)
        self.component_area.setGeometry(QtCore.QRect(580, 0, 1300, 900))

        self.stacked_layout = QStackedLayout(self.component_area)
        self.depth_camera_page = DepthCameraPage(self, (0, 0), (1300, 900))
        self.led_module_page = LEDModulePage(self, (0, 0), (1300, 900))

        self.stacked_layout.addWidget(QWidget(self))
        self.stacked_layout.addWidget(self.depth_camera_page)
        self.stacked_layout.addWidget(self.led_module_page)

        # 多執行序
        self.thread_pool = QThreadPool()

        self.depth_camera_worker = DepthCameraWorker()
        self.depth_camera_worker.signals.data.connect(self.show_image)

        self.thread_pool.start(self.depth_camera_worker)

        # Led
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.led_handler)
        self.led_status = 0

        # self.thread_pool.start(self.weight_reader_worker)

    def change_component(self, component):
        if component == COMPONENT_NAME.LED:
            self.timer.start()
        else:
            self.timer.close()

        self.stacked_layout.setCurrentIndex(component)

    def show_image(self, img, depth):
        len_y, len_x, _ = img.shape
        rgb_image = QImage(img.data, len_x, len_y, QImage.Format_RGB888)
        depth_image = QtGui.QImage(depth.data, len_x, len_y, QImage.Format_RGB888)

        self.depth_camera_page.image_view.setPixmap(QPixmap.fromImage(rgb_image))
        self.depth_camera_page.depth_view.setPixmap(QPixmap.fromImage(depth_image))

    def led_handler(self):
        self.led_module_page.set_status(self.led_status)
        self.led_status = (self.led_status + 1) % 3

        self.led_signal.emit(self.LED_STATUS[self.led_status])


class DepthCameraPage(QWidget):
    def __init__(self, parent, start, size):
        super(DepthCameraPage, self).__init__()

        self.setParent(parent)

        self.setGeometry(QtCore.QRect(*start, *size))

        # set image area
        self.image_view = View(self, (0, (900 - 480) // 2))
        self.depth_view = View(self, (660, (900 - 480) // 2))


class View(QLabel):
    def __init__(self, parent, start):
        super(View, self).__init__()

        self.setParent(parent)

        self.setScaledContents(True)
        self.setMinimumSize(640, 480)
        self.setPixmap(QPixmap.fromImage(QImage('resource/photo.png')))
        self.setGeometry(QtCore.QRect(*start, self.width(), self.height()))


class LEDModulePage(QWidget):
    FONT = QtGui.QFont('微軟正黑體', 36)
    COLOR_LIST = [
        {
            'name': 'BLUE',
            'color': '#2E75B6'
        },
        {
            'name': 'GREEN',
            'color': '#548235'
        },
        {
            'name': 'RED',
            'color': '#d73131'
        }
    ]

    LABEL_STYLE = """
                QLabel{{
                  color: {color};
                }}"""

    LED_STYLE = """
            QLabel{{
              border-radius: 150px;
              background-color: {color};
            }}"""

    def __init__(self, parent, start, size):
        super(LEDModulePage, self).__init__()

        self.setParent(parent)

        self.setGeometry(QtCore.QRect(*start, *size))

        self.status = ['初始化狀態', '閒置狀態', '忙碌狀態']

        self.label_status = QLabel('', self)
        self.label_status.setFont(self.FONT)
        self.label_status.resize(300, 100)
        self.label_status.setGeometry(
            QtCore.QRect(size[0] // 2 - 150, 100, self.label_status.width(), self.label_status.height()))
        self.label_status.setAlignment(QtCore.Qt.AlignCenter)

        self.led = QLabel('', self)
        self.led.resize(300, 300)
        self.led.setGeometry(
            QtCore.QRect(size[0] // 2 - 150, 300, self.led.width(), self.led.height()))

        self.set_status(0)

    def set_status(self, index):
        self.label_status.setText(self.status[index])
        self.label_status.setStyleSheet(self.LABEL_STYLE.format(**self.COLOR_LIST[index]))

        self.led.setStyleSheet(self.LED_STYLE.format(**self.COLOR_LIST[index]))


class DepthCameraWorkerSignals(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(np.ndarray, np.ndarray)


class DepthCameraWorker(QRunnable):
    def __init__(self):
        super(DepthCameraWorker, self).__init__()

        self.signals = DepthCameraWorkerSignals()
        self.depth_camera = DepthCamera()

    @pyqtSlot()
    def run(self):
        try:
            while True:
                image, depth = self.depth_camera.read()
                if image is not None and depth is not None:
                    rgb_image = np.copy(image[:, :, ::-1])

                    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)
                    depth_colormap = np.copy(depth_colormap[:, :, ::-1])

                    self.signals.data.emit(rgb_image, depth_colormap)
        except:
            logging.error("[DEPTH CAMERA WORKER] catch an exception.", exc_info=True)
        finally:
            self.signals.finished.emit()


class LedWorkerSignals(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(np.ndarray, np.ndarray)


class LedCameraWorker(QRunnable):
    def __init__(self):
        super(LedCameraWorker, self).__init__()

        self.signals = LedWorkerSignals()
        # self.depth_camera = DepthCamera()

        self.count = 0

    @pyqtSlot()
    def run(self):
        try:
            while True:
                self.count += 1
                self.signals.data.emit(self.count)
                time.sleep(1)
        except:
            logging.error("[DEPTH CAMERA WORKER] catch an exception.", exc_info=True)
        finally:
            self.signals.finished.emit()
