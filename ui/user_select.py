from PyQt5 import QtCore
from PyQt5.QtWidgets import QScrollArea, QGridLayout, QWidget


class UserSelect(QScrollArea):
    def __init__(self, **kwargs):
        super(UserSelect, self).__init__()

        self.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1860, 1020))

        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setSpacing(50)

        self.setWidget(self.scrollAreaWidgetContents)
