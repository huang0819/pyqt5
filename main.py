import datetime
import os
import sys

from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout

from fake_data.user_data import USER_DATA
from ui.loading_component import LoadingComponent
from ui.main_page import Ui_MainWindow
from ui.message_component import MessageComponent
from ui.user_button import UserButton
from ui.user_control import UserControl
from ui.user_select import UserSelect
from worker.camera_worker import DepthCameraWorker


class UI_PAGE_NAME:
    USER_SELECT = 0
    USER_CONTROL = 1
    LOADING = 2
    MESSAGE = 3


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.showFullScreen()

        self.user_select = UserSelect()
        self.user_control = UserControl()
        self.init_user_control()
        self.loading_component = LoadingComponent()
        self.message_component = MessageComponent()
        self.message_component.close_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        self.qls = QStackedLayout()
        self.qls.addWidget(self.user_select)
        self.qls.addWidget(self.user_control)
        self.qls.addWidget(self.loading_component)
        self.qls.addWidget(self.message_component)

        self.main_window.verticalLayout.addLayout(self.qls)

        self.set_title_text('XX國小X年X班')

        self.user_buttons = []
        self.init_user_buttons()

        # 多執行序
        self.thread_pool = QThreadPool()
        self.depth_camera_worker = DepthCameraWorker()
        self.depth_camera_worker.signals.data.connect(self.show_image)

        self.thread_pool.start(self.depth_camera_worker)

        # self.frame_num = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.save_file)

        # Params
        self.user_data = None
        self.save_type = None
        self.save_folder = 'record'

    def init_user_buttons(self):
        self.user_buttons = []
        for (index, user_data) in enumerate(USER_DATA):
            self.user_buttons.append(UserButton(data=user_data, index=index))
            self.user_buttons[index].resize(self.user_buttons[index].sizeHint())
            self.user_select.gridLayout.addWidget(self.user_buttons[index], index // 5, index % 5, 1, 1)
            self.user_buttons[index].user_click_signal.connect(self.user_button_click_handler)

    def init_user_control(self):
        self.user_control.button_click_signal.connect(self.user_control_handler)

    def set_title_text(self, text):
        self.main_window.title.setText(text)

    def user_control_handler(self, save_type):
        self.change_page(UI_PAGE_NAME.LOADING)
        self.loading_component.start()

        self.save_type = save_type

        self.timer.start()

    def save_file(self):
        file_name = '{}_{}_{}'.format(self.user_data['id'], self.save_type, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        file_path = os.path.join(self.save_folder, '{}.npz'.format(file_name))

        self.depth_camera_worker.depth_camera.save_file(file_path)
        self.timer.stop()
        print(f'save file {file_name}')

        self.change_page(UI_PAGE_NAME.MESSAGE)

        self.user_data = None
        self.save_type = None

    def change_page(self, page):
        if page == UI_PAGE_NAME.USER_SELECT:
            self.set_title_text(f"XX國小X年X班")
        elif page == UI_PAGE_NAME.USER_CONTROL:
            self.set_title_text(f"您好，{self.user_data['name']}同學")
        elif page == UI_PAGE_NAME.MESSAGE:
            self.message_component.start()

        self.qls.setCurrentIndex(page)

    def user_button_click_handler(self, data):
        self.user_data = data
        self.change_page(UI_PAGE_NAME.USER_CONTROL)

    def show_image(self, img):
        len_y, len_x, _ = img.shape  # 取得影像尺寸

        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)

        # 建立 Qimage 物件 (RGB格式)
        qimg = QImage(img.data, len_x, len_y, QImage.Format_RGB888)

        self.user_control.image_view.setPixmap(QPixmap.fromImage(qimg))

        # Frame Rate
        # if self.frame_num == 0:
        #     self.time_start = time.time()
        # if self.frame_num >= 0:
        #     self.frame_num += 1
        #     self.t_total = time.time() - self.time_start
        #     if self.frame_num % 100 == 0:
        #         self.frame_rate = float(self.frame_num) / self.t_total
        #         print(self.frame_rate)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
