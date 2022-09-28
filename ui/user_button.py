from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel


class UserButtonStyle:
    BLUE = 0
    GREEN = 1

    STYLE = {
        BLUE: {
            'user_img_path': r'resource/user_blue.png',
            'font_color': '#2E75B6'
        },
        GREEN: {
            'user_img_path': r'resource/user_green.png',
            'font_color': '#548235'
        }
    }


class UserButton(QWidget):
    user_click_signal = pyqtSignal(object)

    def __init__(self, **kwargs):
        super(UserButton, self).__init__()

        self.data = kwargs['data']
        self.index = kwargs['index']

        self.resize(300, 300)

        self.layout = QVBoxLayout()

        style = UserButtonStyle.STYLE[self.index % 2]

        self.button = QPushButton('', self)
        self.button.setIcon(QtGui.QIcon(style['user_img_path']))
        self.button.setIconSize(QtCore.QSize(300, 300))
        self.button.setMaximumSize(300, 300)
        self.button.setStyleSheet("border: none")

        self.label = QLabel(self.data['name'], self)
        self.label.setStyleSheet(f"color: {style['font_color']}; font-weight: bold;")
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(32)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMaximumSize(300, 48)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.button.clicked.connect(self.button_click_handler)

    def button_click_handler(self):
        self.user_click_signal.emit(self.data)
