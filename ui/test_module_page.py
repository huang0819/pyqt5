import json
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QLabel, QFrame, QGridLayout

import logging
import cv2
import numpy as np

from utils.depth_camera import DepthCamera
from utils.led import LedController
from utils.weight_reader import WeightReader


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

    def __init__(self, config):
        super(TestModulePage, self).__init__()
        self.config = config

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 1040)

        self.btn_depth_camera = Button(self, '深度攝影機', (0, 0), (500, 200))
        self.btn_depth_camera.clicked.connect(lambda: self.change_component(COMPONENT_NAME.DEPTH_CAMERA))
        self.btn_led = Button(self, 'LED模組', (0, 300), (500, 200))
        self.btn_led.clicked.connect(lambda: self.change_component(COMPONENT_NAME.LED))
        self.btn_weight = Button(self, '重量感測器', (0, 600), (500, 200))
        self.btn_weight.clicked.connect(lambda: self.change_component(COMPONENT_NAME.WEIGHT))

        self.component_area = QWidget(self)
        self.component_area.setGeometry(QtCore.QRect(580, 0, 1300, 900))

        self.stacked_layout = QStackedLayout(self.component_area)
        self.depth_camera_page = DepthCameraPage(self, (0, 0), (1300, 900))
        self.led_module_page = LEDModulePage(self, (0, 0), (1300, 900))
        self.weight_module_page = WeightModulePage(self, (0, 0), (1300, 900))
        self.weight_module_page.calibrate_signal.connect(self.calibrate)

        self.stacked_layout.addWidget(QWidget(self))
        self.stacked_layout.addWidget(self.depth_camera_page)
        self.stacked_layout.addWidget(self.led_module_page)
        self.stacked_layout.addWidget(self.weight_module_page)

        # 多執行序
        # self.thread_pool = QThreadPool()
        #
        # self.depth_camera_worker = DepthCameraWorker()
        # self.depth_camera_worker.signals.data.connect(self.show_image)
        #
        # self.thread_pool.start(self.depth_camera_worker)
        #
        # # Led
        # self.led_controller = LedController(
        #     channel_r=self.config.getint('led', 'channel_r'),
        #     channel_b=self.config.getint('led', 'channel_b'),
        #     channel_g=self.config.getint('led', 'channel_g')
        # )

        self.led_timer = QTimer()
        self.led_timer.setInterval(1000)
        # self.led_timer.timeout.connect(self.led_handler)
        self.led_status = 0

        # Depth
        self.weight_reader = WeightReader(
            dout=self.config.getint('weight', 'channel_data'),
            pd_sck=self.config.getint('weight', 'channel_clk'),
            reference_unit=self.config.getfloat('weight', 'reference_unit')
        )

        self.weight_timer = QTimer()
        self.weight_timer.setInterval(100)
        self.weight_timer.timeout.connect(self.weight_handler)
        self.weight = 0

    def change_component(self, component):
        if component == COMPONENT_NAME.LED:
            self.led_timer.start()
        else:
            self.led_timer.stop()
        if component == COMPONENT_NAME.WEIGHT:
            self.weight_timer.start()
        else:
            self.weight_timer.stop()

        self.stacked_layout.setCurrentIndex(component)

    def show_image(self, img, depth):
        len_y, len_x, _ = img.shape
        rgb_image = QImage(img.data, len_x, len_y, QImage.Format_RGB888)
        depth_image = QtGui.QImage(depth.data, len_x, len_y, QImage.Format_RGB888)

        self.depth_camera_page.image_view.setPixmap(QPixmap.fromImage(rgb_image))
        self.depth_camera_page.depth_view.setPixmap(QPixmap.fromImage(depth_image))

    def led_handler(self):
        self.led_module_page.set_status(self.led_status)
        self.led_controller.set_value(*json.loads(self.config.get('led', self.LED_STATUS[self.led_status])))
        self.led_status = (self.led_status + 1) % 3

    def weight_handler(self):
        self.weight_reader.read()
        self.weight_module_page.set_weight(self.weight_reader.val)

    def calibrate(self):
        self.weight_timer.stop()
        self.weight_reader.reset()

        read_times = 60

        origin_val = 0
        for i in range(read_times):
            self.weight_reader.read(debug=True)
            self.weight_module_page.set_weight(self.weight_reader.val)
            origin_val += self.weight_reader.val
            time.sleep(0.1)

        origin_val /= read_times

        print(origin_val)


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


class WeightModulePage(QWidget):
    calibrate_signal = pyqtSignal()

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

    COMPONENT_CLEAR = 0
    COMPONENT_INPUT = 1
    COMPONENT_WAIT = 1

    def __init__(self, parent, start, size):
        super(WeightModulePage, self).__init__()

        self.setParent(parent)

        self.setGeometry(QtCore.QRect(*start, *size))

        # sensor value display
        self.weight_info = '重量: {:.3f} 公克'
        self.label_weight = QLabel(self.weight_info.format(0), self)
        self.label_weight.setFont(self.FONT)
        self.label_weight.resize(800, 100)
        self.label_weight.setGeometry(
            QtCore.QRect(size[0] // 2 - 400, 0, self.label_weight.width(), self.label_weight.height()))
        self.label_weight.setAlignment(QtCore.Qt.AlignCenter)

        # title of calibrate area
        self.label_calibrate = QLabel('感測器校正', self)
        self.label_calibrate.setFont(self.FONT)
        self.label_calibrate.resize(self.label_calibrate.sizeHint())
        self.label_calibrate.setGeometry(
            QtCore.QRect(0, 130, self.label_calibrate.width(), self.label_calibrate.height()))
        self.label_calibrate.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet('background-color: #4472C4')
        self.line.setGeometry(
            QtCore.QRect(0, 130 + self.label_calibrate.height(), self.width() - 20, 3))

        # calibrate area
        self.calibrate_area = QWidget(self)
        self.calibrate_area.setGeometry(QtCore.QRect(0, 140 + self.label_weight.height(), self.width(),
                                                     self.height() - 140 + self.label_weight.height()))
        self.stacked_layout = QStackedLayout(self.calibrate_area)

        # clear area
        self.calibrate_clear_widget = QWidget(self)
        self.label_clear = QLabel('請將拍攝平面物體全部移除後，按下 "開始校正" 按鈕', self.calibrate_clear_widget)
        self.label_clear.setWordWrap(True)
        self.label_clear.setFont(QtGui.QFont('微軟正黑體', 32))
        self.label_clear.resize(1300, 100)
        self.label_clear.setGeometry(
            QtCore.QRect(0, 0, self.label_clear.width(), self.label_clear.height()))
        self.label_clear.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_clear.setStyleSheet(self.LABEL_STYLE.format(**self.COLOR_LIST[2]))

        self.btn_clear = Button(self.calibrate_clear_widget, '開始校正', (size[0] // 2 - 250, 280), (500, 200))
        self.btn_clear.setStyleSheet(self.btn_clear.BTN_STYLE.format(**self.btn_clear.GREEN))
        self.btn_clear.clicked.connect(self.calibrate)

        # input area
        self.calibrate_input_widget = QWidget(self)

        # weight of calibrate object
        self.calibrate_weight = 0
        self.calibrate_weight_info = '請輸入校正物之重量: {} 公克'
        self.label_calibrate_weight = QLabel(self.calibrate_weight_info.format(self.calibrate_weight),
                                             self.calibrate_input_widget)
        self.label_calibrate_weight.setFont(self.FONT)
        self.label_calibrate_weight.resize(self.width(), 80)
        self.label_calibrate_weight.setGeometry(
            QtCore.QRect(0, 0, self.label_calibrate_weight.width(), self.label_calibrate_weight.height()))
        self.label_calibrate_weight.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.key_board = KeyBoard(self.calibrate_input_widget, (
            size[0] // 2 - 400, 20 + self.label_calibrate_weight.height()), (800, 560))

        self.key_board.output_signal.connect(self.set_calibrate_weight)
        self.key_board.calibrate_signal.connect(self.calibrate)

        self.stacked_layout.addWidget(self.calibrate_clear_widget)
        self.stacked_layout.addWidget(self.calibrate_input_widget)

    def set_weight(self, weight):
        self.label_weight.setText(self.weight_info.format(weight))

    def set_calibrate_weight(self, weight):
        self.calibrate_weight = weight
        self.label_calibrate_weight.setText(self.calibrate_weight_info.format(weight))

    def calibrate(self):
        self.calibrate_signal.emit()
        print(float(self.calibrate_weight))


class KeyBoard(QWidget):
    output_signal = pyqtSignal(str)
    calibrate_signal = pyqtSignal()
    FONT = QtGui.QFont('微軟正黑體', 36)
    COMMANDS_NUM = 0
    COMMANDS_DOT = 1
    COMMANDS_DEL = 2
    COMMANDS_CAL = 3

    def __init__(self, parent, start, size):
        super(KeyBoard, self).__init__()

        self.setParent(parent)
        self.setGeometry(QtCore.QRect(*start, *size))

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(20)

        self.output = ''

        self.btn_nums = []

        for i in range(10):
            self.btn_nums.append(KeyBoardBtn(str(i), (150, 120), self.COMMANDS_NUM, data=i))
            self.btn_nums[i].clicked_signal.connect(self.command_handler)

            if i == 0:
                self.grid_layout.addWidget(self.btn_nums[i], 3, 0, 1, 2)
            else:
                self.grid_layout.addWidget(self.btn_nums[i], (i - 1) // 3, (i - 1) % 3, 1, 1)

        self.bnt_dot = KeyBoardBtn('.', (150, 120), self.COMMANDS_DOT, data=None)
        self.bnt_dot.clicked_signal.connect(self.command_handler)
        self.grid_layout.addWidget(self.bnt_dot, 3, 2, 1, 1)

        self.bnt_del = KeyBoardBtn('Del', (150, 260), self.COMMANDS_DEL, data=None)
        self.bnt_del.clicked_signal.connect(self.command_handler)
        self.grid_layout.addWidget(self.bnt_del, 0, 3, 2, 1)

        self.bnt_calibrate = KeyBoardBtn('校\n正', (150, 260), self.COMMANDS_CAL, data=None)
        self.bnt_calibrate.clicked_signal.connect(self.command_handler)
        self.grid_layout.addWidget(self.bnt_calibrate, 2, 3, 2, 1)

    def command_handler(self, obj):
        if obj['cmd'] == self.COMMANDS_NUM:
            self.output += str(obj['data'])
        elif obj['cmd'] == self.COMMANDS_DOT:
            if self.output.find('.') == -1:
                self.output += '.'
        elif obj['cmd'] == self.COMMANDS_DEL:
            if len(self.output) > 0:
                self.output = self.output[:-1]
        elif obj['cmd'] == self.COMMANDS_CAL:
            self.calibrate_signal.emit()

        self.output_signal.emit(self.output)


class KeyBoardBtn(QPushButton):
    FONT = QtGui.QFont('微軟正黑體', 36)
    clicked_signal = pyqtSignal(dict)

    def __init__(self, text, size, command, data):
        super(KeyBoardBtn, self).__init__()

        self.command = command
        self.data = data

        self.setText(text)
        self.setFont(self.FONT)
        self.setMinimumSize(*size)
        self.clicked.connect(self.btn_handler)

    def btn_handler(self):
        self.clicked_signal.emit({
            'cmd': self.command,
            'data': self.data
        })
