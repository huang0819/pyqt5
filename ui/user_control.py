from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel


class UserControl(QWidget):
    # user_click_signal = pyqtSignal(object)

    def __init__(self, **kwargs):
        super(UserControl, self).__init__()

        self.layout = QVBoxLayout()

        # self.button = QPushButton('', self)
        # self.button.setIcon(QtGui.QIcon(style['user_img_path']))
        # self.button.setIconSize(QtCore.QSize(300, 300))
        # self.button.setMaximumSize(300, 300)
        # self.button.setStyleSheet("border: none")

        self.label = QLabel('', self)
        # self.label.setStyleSheet(f"color: {style['font_color']}; font-weight: bold;")
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(32)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMaximumSize(300, 48)
        self.label.setText('請將餐盤確實放置於拍攝平面')

        # self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    #     self.button.clicked.connect(self.button_click_handler)
    #
    # def button_click_handler(self):
    #     self.user_click_signal.emit(self.data)
