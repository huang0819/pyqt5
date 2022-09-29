from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QSpacerItem


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
        font: bold 58px 微軟正黑體;
        border-width: 1px;
        border-radius: 10px;
        border-color: transparent;
    }}
    QPushButton:pressed {{
        background-color: {pressed_color};
    }}"""


class UserControl(QWidget):
    button_click_signal = pyqtSignal(int)
    button_return_signal = pyqtSignal()

    def __init__(self, **kwargs):
        super(UserControl, self).__init__()

        # set layout
        self.layout = QGridLayout()
        self.layout.setSpacing(50)

        # set hint message
        self.hint_message = QLabel('請將餐盤確實放置於拍攝平面', self)
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(36)
        self.hint_message.setFont(font)
        self.hint_message.setStyleSheet("color: #C00000; font-weight: bold;")
        self.hint_message.setAlignment(QtCore.Qt.AlignLeft)
        self.hint_message.resize(self.hint_message.sizeHint())
        self.layout.addWidget(self.hint_message, 0, 0, 1, 3)

        # spacer
        self.v_spacer = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(self.v_spacer, 1, 0, 1, 1)

        # set image area
        self.image_view = QLabel('')
        self.image_view.setMinimumSize(640, 480)
        qimg = QImage('resource/photo.png')
        self.image_view.setPixmap(QPixmap.fromImage(qimg))
        self.layout.addWidget(self.image_view, 2, 0, 1, 1)

        # set before meal btn
        self.before_meal_button = QPushButton('用餐前紀錄', self)
        self.before_meal_button.setMaximumSize(500, 300)
        self.before_meal_button.setStyleSheet(BTN_STYLE.format(**COLOR_MAP.BLUE))
        self.before_meal_button.clicked.connect(lambda: self.button_click_handler(0))
        self.layout.addWidget(self.before_meal_button, 2, 1, 1, 1)

        # set after meal btn
        self.after_meal_button = QPushButton('用餐後紀錄', self)
        self.after_meal_button.setMaximumSize(500, 300)
        self.after_meal_button.setStyleSheet(BTN_STYLE.format(**COLOR_MAP.GREEN))
        self.after_meal_button.clicked.connect(lambda: self.button_click_handler(1))
        self.layout.addWidget(self.after_meal_button, 2, 2, 1, 1)

        # spacer
        # self.v_spacer = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.layout.addItem(self.v_spacer, 3, 0, 1, 1)

        # return btn
        self.return_button = QPushButton('', self)
        self.return_button.setMaximumSize(200, 200)
        self.return_button.setIcon(QtGui.QIcon(r'resource/previous.png'))
        self.return_button.setIconSize(QtCore.QSize(200, 200))
        self.return_button.setStyleSheet('background-color: transparent')
        self.return_button.clicked.connect(self.button_return_signal)
        self.layout.addWidget(self.return_button, 3, 3, 1, 1)

        # set layout
        self.setLayout(self.layout)

    def button_click_handler(self, save_type):
        self.button_click_signal.emit(save_type)
