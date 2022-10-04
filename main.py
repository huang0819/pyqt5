import datetime
import json
import os
import sys
import logging
import configparser

from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout

from fake_data.user_data import USER_DATA

from ui.config import UI_PAGE_NAME
from ui.loading_component import LoadingComponent
from ui.main_page import Ui_MainWindow
from ui.message_component import MessageComponent
from ui.user_control import UserControl
from ui.user_select import UserSelect

from utils.led import LedController

from worker.camera_worker import DepthCameraWorker


class MainWindow(QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.config = config

        # led control
        self.led_controller = LedController(
            channel_r=self.config.get('led', 'channel_r'),
            channel_b=self.config.get('led', 'channel_g'),
            channel_g=self.config.get('led', 'channel_b')
        )
        self.led_controller.set_value(*json.loads(config.get('led', 'state_setup')))

        # ui setup
        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.main_window.button_return_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        self.showFullScreen()

        # user select page
        self.user_select = UserSelect()
        self.user_select.set_user_btn_page(USER_DATA[:16])
        self.user_select.user_btn_click_signal.connect(self.user_button_handler)

        # user control page
        self.user_control = UserControl()
        self.user_control.button_click_signal.connect(self.user_control_handler)

        # loading component
        self.loading_component = LoadingComponent()

        # message component
        self.message_component = MessageComponent()
        self.message_component.close_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        # stack layout
        self.qls = QStackedLayout()
        self.qls.addWidget(self.user_select)
        self.qls.addWidget(self.user_control)
        self.qls.addWidget(self.loading_component)
        self.qls.addWidget(self.message_component)

        self.main_window.verticalLayout.addLayout(self.qls)

        self.set_title_text('XX國小X年X班')

        self.user_buttons = []

        # 多執行序
        self.thread_pool = QThreadPool()
        self.depth_camera_worker = DepthCameraWorker()
        self.depth_camera_worker.signals.data.connect(self.show_image)

        self.thread_pool.start(self.depth_camera_worker)

        # self.frame_num = 0

        # 計數器，間隔一秒再存資料
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.save_file)

        # Params
        self.user_data = None
        self.save_type = None
        self.save_folder = 'record'

        self.led_controller.set_value(*json.loads(config.get('led', 'state_idle')))

    def set_title_text(self, text):
        self.main_window.title.setText(text)

    def user_control_handler(self, save_type):
        self.change_page(UI_PAGE_NAME.LOADING)
        self.save_type = save_type

        self.led_controller.set_value(*json.loads(config.get('led', 'state_busy')))
        self.timer.start()

    def save_file(self):
        self.timer.stop()

        file_name = '{}_{}_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), self.user_data['id'], self.save_type)
        file_path = os.path.join(self.save_folder, '{}.npz'.format(file_name))

        self.depth_camera_worker.depth_camera.save_file(file_path)

        logging.info(f'save file: {file_name}')

        self.change_page(UI_PAGE_NAME.MESSAGE)

        self.user_data = None
        self.save_type = None

        self.led_controller.set_value(*json.loads(config.get('led', 'state_idle')))

    def change_page(self, page):
        if page == UI_PAGE_NAME.USER_SELECT:
            self.set_title_text(f"XX國小X年X班")
            self.main_window.return_button.hide()
        elif page == UI_PAGE_NAME.USER_CONTROL:
            self.set_title_text(f"您好，{self.user_data['name']}同學")
            self.main_window.return_button.show()
        elif page == UI_PAGE_NAME.LOADING:
            self.loading_component.start()
        elif page == UI_PAGE_NAME.MESSAGE:
            self.message_component.start()

        self.qls.setCurrentIndex(page)

    def user_button_handler(self, data):
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
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    DATE_FORMAT = '%Y%m%d %H:%M:%S'
    # if args.show_log:
    #     log_file_name = '{}_log.log'.format(datetime.datetime.now().strftime("%Y%m%d"))
    #     log_file_path = os.path.join('logs', log_file_name)
    # else:
    #     log_file_path = None

    log_file_path = None
    logging.basicConfig(level=logging.DEBUG, filename=log_file_path, filemode='a', format=FORMAT)

    logging.info('*** Start application ***')

    config = configparser.ConfigParser()
    config.read(r'config/config.ini', encoding='utf-8')

    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec_())

