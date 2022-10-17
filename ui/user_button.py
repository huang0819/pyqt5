from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class UserButton(QWidget):
    user_click_signal = pyqtSignal(object)

    BLUE = 0
    GREEN = 1

    STYLE = {
        BLUE: {
            'img_color_name': 'blue',
            'font_color': '#2E75B6'
        },
        GREEN: {
            'img_color_name': 'green',
            'font_color': '#548235'
        }
    }

    def __init__(self, **kwargs):
        super(UserButton, self).__init__()

        self.data = kwargs['data']
        self.index = kwargs['index']

        self.layout = QVBoxLayout()

        style = self.STYLE[self.index % 2]

        self.button = QPushButton('', self)
        self.button.setMinimumSize(300, 300)
        self.button.setStyleSheet("""
            QPushButton{{
                background-color: transparent; 
                border: none; 
                image: url(resource/user_{button_type}.png)
            }}
            QPushButton:pressed {{
                background-color: transparent; 
                border: none; 
                image: url(resource/user_{button_type}_pressed.png)
            }}
        """.format(button_type=style['img_color_name']))

        self.label = QLabel(self.data['name'], self)
        self.label.setStyleSheet(f"color: {style['font_color']}")
        self.label.setFont(QtGui.QFont('微軟正黑體', 42))
        self.label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.label.resize(300, 50)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.button.clicked.connect(self.button_click_handler)

    def button_click_handler(self):
        self.user_click_signal.emit(self.data)
