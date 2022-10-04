import datetime
import json
import os
import queue
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
from worker.weight_worker import WeightReaderWorker
from worker.upload_worker import UploadWorker


class MainWindow(QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.config = config

        # Create data folder
        self.save_folder = os.path.join(self.config.get('path', 'save_dir'), datetime.datetime.now().strftime("%Y%m%d"))
        if not os.path.isdir(self.save_folder):
            logging.info('[MAIN] create data folder: {}'.format(self.save_folder))
            os.makedirs(self.save_folder, exist_ok=True)

        self.json_path = os.path.join(self.save_folder, 'data.json')

        # led control
        self.led_controller = LedController(
            channel_r=self.config.getint('led', 'channel_r'),
            channel_b=self.config.getint('led', 'channel_b'),
            channel_g=self.config.getint('led', 'channel_g')
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

        self.weight_reader_worker = WeightReaderWorker(
            channel_data=self.config.getint('weight', 'channel_data'),
            channel_clk=self.config.getint('weight', 'channel_clk'),
            reference_unit=self.config.getfloat('weight', 'reference_unit')
        )

        self.thread_pool.start(self.depth_camera_worker)
        self.thread_pool.start(self.weight_reader_worker)

        # 計數器，間隔一秒再存資料
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.save_file)

        # Params
        self.user_data = None
        self.save_type = None

        self.data_queue = queue.Queue()

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

        file_name = '{}_{}_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), self.user_data['id'],
                                      self.save_type)
        file_path = os.path.join(self.save_folder, '{}.npz'.format(file_name))

        self.depth_camera_worker.depth_camera.save_file(file_path)

        logging.info(f'[MAIN] save file: {file_name}')

        data = {
            'payload': {
                'user_id': self.user_data['id'],
                'weight': self.weight_reader_worker.weight_reader.val,
                'meal_date': datetime.datetime.now().strftime('%Y-%m-%d')
            },
            'file_path': file_path,
            'file_name': file_name
        }

        upload_worker = UploadWorker(base_url=self.config.get('api', 'base_url'), data=data)
        upload_worker.setAutoDelete(True)
        self.thread_pool.start(upload_worker)

        self.save_json({
            file_name: {
                'user_id': self.user_data['id'],
                'weight': self.weight_reader_worker.weight_reader.val,
                'save_type': self.save_type
                # 'is_upload': is_upload
            }
        })

        logging.info('[MAIN] save json')

        self.change_page(UI_PAGE_NAME.MESSAGE)

        self.user_data = None
        self.save_type = None

        self.led_controller.set_value(*json.loads(config.get('led', 'state_idle')))

    def save_json(self, data):
        if os.path.isfile(self.json_path):
            with open(self.json_path) as json_file:
                json_data = json.load(json_file)
        else:
            json_data = {}

        json_data.update(data)

        with open(self.json_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=4)

    def change_page(self, page):
        self.main_window.return_button.hide()

        if page == UI_PAGE_NAME.USER_SELECT:
            self.set_title_text(f"XX國小X年X班")
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
        len_y, len_x, _ = img.shape
        qimg = QImage(img.data, len_x, len_y, QImage.Format_RGB888)
        self.user_control.image_view.setPixmap(QPixmap.fromImage(qimg))

    def exit_handler(self):
        self.led_controller.clear_GPIO()
        logging.info('*** Close application ***')


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
