from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout


class COLOR_MAP:
    GREEN = {
        'common_color': '#548235',
        'pressed_color': '#A9D18E'
    }
    BLUE = {
        'common_color': '#2E75B6',
        'pressed_color': '#9DC3E6'
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


class UserControl(QWidget):
    ICON_SIZE = 64

    button_click_signal = pyqtSignal(int)

    def __init__(self):
        super(UserControl, self).__init__()

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 900)

        # hint icon
        self.hint_icon = QLabel(self)
        self.hint_icon.setPixmap(QPixmap('resource/warning.png').scaled(self.ICON_SIZE, self.ICON_SIZE, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.hint_icon.resize(self.ICON_SIZE, self.ICON_SIZE)
        self.hint_icon.setGeometry(QtCore.QRect((100-self.ICON_SIZE)//2, (100-self.ICON_SIZE)//2, self.hint_icon.width(), self.hint_icon.height()))

        # hint message
        self.hint_message = QLabel('請將餐盤確實放置於拍攝平面', self)
        font = QtGui.QFont('微軟正黑體', 36)
        self.hint_message.setFont(font)
        self.hint_message.setStyleSheet('color: #C00000')
        self.hint_message.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        self.hint_message.resize(self.hint_message.sizeHint())
        self.hint_message.setFixedHeight(100)
        self.hint_message.setGeometry(QtCore.QRect(100, 0, self.hint_message.width(), self.hint_message.height()))

        # set image area
        self.image_view = QLabel(self)
        self.image_view.setScaledContents(True)
        self.image_view.setMinimumSize(640, 480)
        self.image_view.setPixmap(QPixmap.fromImage(QImage('resource/photo.png')))
        self.image_view.setGeometry(QtCore.QRect(0, 130, int(640*1.5), int(480*1.5)))

        # button area
        self.btn_area = QWidget(self)
        self.btn_area.setGeometry(QtCore.QRect(1880//2 + 50, 0, 1880//2 - 50, 900))

        # set layout
        self.layout = QGridLayout(self.btn_area)
        self.layout.setSpacing(50)

        # set before meal btn
        self.before_meal_button = QPushButton('用餐前紀錄', self)
        self.before_meal_button.setMaximumSize(400, 300)
        self.before_meal_button.setStyleSheet(BTN_STYLE.format(**COLOR_MAP.BLUE))
        self.before_meal_button.clicked.connect(lambda: self.button_click_handler(0))
        self.layout.addWidget(self.before_meal_button, 0, 0, 1, 1)

        # set after meal btn
        self.after_meal_button = QPushButton('用餐後紀錄', self)
        self.after_meal_button.setMaximumSize(400, 300)
        self.after_meal_button.setStyleSheet(BTN_STYLE.format(**COLOR_MAP.GREEN))
        self.after_meal_button.clicked.connect(lambda: self.button_click_handler(1))
        self.layout.addWidget(self.after_meal_button, 1, 0, 1, 1)

        # set layout
        self.btn_area.setLayout(self.layout)

    def button_click_handler(self, save_type):
        self.button_click_signal.emit(save_type)
