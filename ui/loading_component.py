from PyQt5 import QtCore
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class LoadingComponent(QWidget):
    def __init__(self, **kwargs):
        super(LoadingComponent, self).__init__()

        # set layout
        self.layout = QVBoxLayout()

        # Create loading view
        self.loading_view = QLabel('', self)
        self.loading_view.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

        # Loading the GIF
        self.movie = QMovie(r'resource/loading.gif')
        self.loading_view.setMovie(self.movie)
        self.loading_view.resize(self.loading_view.sizeHint())

        self.layout.addWidget(self.loading_view)

        # Create message
        self.message = QLabel('資料收集中，請稍後', self)
        self.message.setStyleSheet('color: #2E75B6; font: 36px 微軟正黑體;')
        self.message.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.message)

        self.setLayout(self.layout)

    def start(self):
        self.movie.start()

    def stop(self):
        self.movie.stop()
