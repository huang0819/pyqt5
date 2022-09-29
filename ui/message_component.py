from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class MessageComponent(QWidget):
    close_signal = pyqtSignal()

    def __init__(self, **kwargs):
        super(MessageComponent, self).__init__()

        # set layout
        self.layout = QVBoxLayout()

        # Create loading view
        self.image_view = QLabel('', self)
        self.image_view.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.image_view.setMinimumSize(200, 200)
        qimg = QImage('resource/complete.png')
        self.image_view.setPixmap(QPixmap.fromImage(qimg))

        self.layout.addWidget(self.image_view)

        # Create message
        self.message = QLabel('資料收集完成\n可將餐盤取出', self)
        self.message.setStyleSheet('color: #70AD47; font: bold 48px 微軟正黑體;')
        self.message.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.message)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.close)

    def start(self):
        self.timer.start()

    def close(self):
        self.close_signal.emit()
        self.timer.stop()
