from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton


class Ui_MainWindow(QObject):
    button_return_signal = pyqtSignal()
    button_setting_signal = pyqtSignal()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("AI Food Assessment Data Collect Tool")
        MainWindow.resize(1920, 1080)

        self.centralwidget = QWidget(MainWindow)

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 1880, 1040))

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(20)

        self.title = QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(48)
        self.title.setFixedHeight(100)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.title)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet('background-color: #4472C4')

        # return btn
        self.return_button = QPushButton('', MainWindow)
        self.return_button.setMaximumSize(100, 100)
        self.return_button.setIcon(QtGui.QIcon(r'resource/return.png'))
        self.return_button.setIconSize(QtCore.QSize(100, 100))
        self.return_button.setStyleSheet('background-color: #f0f0f0; border: none')
        self.return_button.setGeometry(QtCore.QRect(20, 20, 100, 100))
        self.return_button.clicked.connect(self.button_return_signal)
        self.return_button.hide()

        # setting btn
        self.setting_button = QPushButton('', MainWindow)
        self.setting_button.setMaximumSize(100, 100)
        self.setting_button.setStyleSheet('background-color: #f0f0f0; border: none')
        self.setting_button.setGeometry(QtCore.QRect(1780, 20, 100, 100))
        self.setting_button.clicked.connect(self.button_setting_signal)

        self.verticalLayout.addWidget(self.line)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "TextLabel"))
