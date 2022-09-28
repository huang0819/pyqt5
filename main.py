import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QStackedLayout
from data_collect import Ui_MainWindow
import time

from utils.depth_camera import DepthCamera


class Panel(QWidget):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()

        background_color = {'background-color': f"{kwargs['background_color']};"}

        style = f"QWidget{background_color}".replace("'", '')

        self.setStyleSheet(style)

        onePanel_layout = QHBoxLayout()
        qlabel = QLabel(kwargs['label'])
        qlabel.setStyleSheet("color: blue; font-weight: bold; font-size: 24px")
        onePanel_layout.addWidget(qlabel)

        self.setLayout(onePanel_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        one = Panel(label='test 1', background_color='#66CCFF')
        two = Panel(label='test 2', background_color='#66FFCC')
        three = Panel(label='test 3', background_color='#EE0000')

        qls = QStackedLayout()
        qls.addWidget(one)
        qls.addWidget(two)
        qls.addWidget(three)

        self.ui.verticalLayout.addLayout(qls)

        # self.ui.pushButton.clicked.connect(self.test)

        self.ui.pushButton.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton, qls))
        self.ui.pushButton_2.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton_2, qls))
        self.ui.pushButton_3.clicked.connect(lambda: self.buttonIsClicked(self.ui.pushButton_3, qls))

        # 多執行序
        self.thread = Worker()
        self.thread.finish.connect(self.thread.clear_data)

        self.thread.start()

    def test(self):
        data = {
            'id': 0,
            'name': 'test'
        }
        self.ui.label.setText(data['name'])
        self.thread.set(**data)
        # self.thread.quit()

    def buttonIsClicked(self, button, qls):
        print(button.text())
        dic = {
            "1": 0,
            "2": 1,
            "3": 2
        }
        index = dic[button.text()]
        qls.setCurrentIndex(index)


class Worker(QThread):
    finish = pyqtSignal()

    data = None

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def set(self, **kwargs):
        self.data = kwargs

    def clear_data(self):
        self.data = None

    def run(self):
        # while True:
        #     if self.data is not None:
        #         print(self.data)
        #
        #         self.finish.emit()
        #         time.sleep(1)
        #     pass
        dc = DepthCamera('record', debug=True)
        dc.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
