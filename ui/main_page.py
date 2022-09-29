from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("AI Food Assessment Data Collect Tool")
        MainWindow.resize(1920, 1080)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 1880, 1040))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(20)

        self.title = QLabel(self.verticalLayoutWidget)
        self.title.setMaximumSize(QtCore.QSize(16777215, 150))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(48)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")

        self.verticalLayout.addWidget(self.title)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet('background-color: #4472C4')

        self.verticalLayout.addWidget(self.line)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "TextLabel"))
        # self.pushButton.setText(_translate("MainWindow", "1"))
        # self.pushButton_2.setText(_translate("MainWindow", "2"))
        # self.pushButton_3.setText(_translate("MainWindow", "3"))
        # self.pushButton_7.setText(_translate("MainWindow", "PushButton"))
        # self.pushButton_6.setText(_translate("MainWindow", "PushButton"))
        # self.pushButton_4.setText(_translate("MainWindow", "PushButton"))
        # self.pushButton_5.setText(_translate("MainWindow", "PushButton"))
        # self.pushButton_9.setText(_translate("MainWindow", "PushButton"))
        # self.pushButton_8.setText(_translate("MainWindow", "PushButton"))

