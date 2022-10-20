import argparse
import configparser
import datetime
import json
import logging
import os
import sys

from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout

from ui.config import UI_PAGE_NAME
from ui.main_page import Ui_MainWindow
from ui.message_component import MessageComponent
from ui.setting_page import SettingPage
from ui.user_control import UserControl
from ui.user_select import UserSelect
from utils.api import Api
from utils.led import LedController, LED_STATUS
from utils.worker import Worker
from worker.camera_worker import DepthCameraWorker
from worker.upload_worker import UploadWorker
from worker.weight_worker import WeightReaderWorker

CODE_VERSION = '1.0.3'

CONFIG_PATH = r'config/config.ini'
USER_LIST_PATH = r'config/user_list.json'

parser = argparse.ArgumentParser()
parser.add_argument('-sl', '--show_log', action='store_true', help='show message in terminal')
args = parser.parse_args()


class MainWindow(QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.config = config
        self.api = Api(config.get('api', 'base_url'))
        self.status = LED_STATUS.SETUP

        # Multi thread
        self.thread_pool = QThreadPool()

        # Create data folder
        self.save_folder = os.path.join(self.config.get('path', 'save_dir'), datetime.datetime.now().strftime("%Y%m%d"))
        if not os.path.isdir(self.save_folder):
            logging.info('[MAIN] create data folder: {}'.format(self.save_folder))
            os.makedirs(self.save_folder, exist_ok=True)

        self.json_path = os.path.join(self.save_folder, 'data.json')

        # Led control
        self.led_controller = LedController(
            channel_r=self.config.getint('led', 'channel_r'),
            channel_b=self.config.getint('led', 'channel_b'),
            channel_g=self.config.getint('led', 'channel_g')
        )
        self.change_status(LED_STATUS.SETUP)

        # UI setup
        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.main_window.button_return_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))
        self.main_window.button_setting_signal.connect(self.set_setting_page_options)
        self.main_window.button_exit_signal.connect(self.exit_handler)

        self.showFullScreen()

        # User select page
        self.user_select = UserSelect()
        self.user_select.user_btn_click_signal.connect(self.user_button_handler)

        # User control page
        self.user_control = UserControl()
        self.user_control.button_click_signal.connect(self.user_control_handler)

        # Loading component
        self.loading_component = MessageComponent(text='處理中，請稍候。', font_size=64, color='#2E75B6', wait_time=0)

        # Complete message component
        self.complete_message = MessageComponent(text='資料收集完成\n可將餐盤取出', image_path='resource/complete.png', font_size=64)
        self.complete_message.close_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        # Init message component
        self.init_message = MessageComponent(text='初始化中，請稍候。', font_size=64, color='#2E75B6', wait_time=0)

        # Error message component
        self.error_message = MessageComponent(text='網路異常，請確認是否有連接網路', font_size=64, color='#C00000', wait_time=0)

        # Setting page
        self.setting_page = SettingPage()
        self.setting_page.save_signal.connect(self.save_handler)

        # Stack layout
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.user_select)
        self.stacked_layout.addWidget(self.user_control)
        self.stacked_layout.addWidget(self.loading_component)
        self.stacked_layout.addWidget(self.complete_message)
        self.stacked_layout.addWidget(self.setting_page)
        self.stacked_layout.addWidget(self.init_message)
        self.stacked_layout.addWidget(self.error_message)

        self.stacked_layout.setCurrentIndex(UI_PAGE_NAME.INIT_MSG)

        self.main_window.verticalLayout.addLayout(self.stacked_layout)

        self.user_buttons = []

        # Setup user select page
        self.set_user_list()
        self.set_title_text(
            f"{self.config.get('school', 'name')}{self.config.getint('school', 'grade')}年{self.config.get('school', 'class')}班")

        # Wait 1 second for saving file
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.save_file)

        # If weight worker not work
        self.pass_timer = QTimer()
        self.pass_timer.setInterval(20000)
        self.pass_timer.timeout.connect(self.pass_weight_init)

        # Thread of initialize module
        self.init_worker = Worker(self.setup_sensors)
        self.init_worker.signals.finished.connect(self.finish_setup_sensors)
        self.init_worker.setAutoDelete(True)
        self.thread_pool.start(self.init_worker)
        self.pass_timer.start()

        # Params
        self.user_data = None
        self.save_type = None
        self.is_upload = 0
        self.is_weight_reader_ok = False

    def change_status(self, status):
        self.status = status
        self.led_controller.set_value(*json.loads(config.get('led', status)))

    def setup_sensors(self):
        self.depth_camera_worker = DepthCameraWorker()
        self.depth_camera_worker.signals.data.connect(self.show_image)

        self.weight_reader_worker = WeightReaderWorker(
            channel_data=self.config.getint('weight', 'channel_data'),
            channel_clk=self.config.getint('weight', 'channel_clk'),
            reference_unit=self.config.getfloat('weight', 'reference_unit')
        )

        self.thread_pool.start(self.depth_camera_worker)
        self.thread_pool.start(self.weight_reader_worker)

        self.self.is_weight_reader_ok = True

    def finish_setup_sensors(self):
        self.change_page(UI_PAGE_NAME.USER_SELECT)
        self.change_status(LED_STATUS.IDLE)

    def pass_weight_init(self):
        logging.info('[MAIN] weight reader not connected')
        self.thread_pool.start(self.depth_camera_worker)
        self.finish_setup_sensors()

    def set_title_text(self, text):
        self.main_window.title.setText(text)

    def user_control_handler(self, save_type):
        self.change_status(LED_STATUS.BUSY)
        self.change_page(UI_PAGE_NAME.LOADING)
        self.save_type = save_type

        self.timer.start()

    def save_file(self):
        self.timer.stop()

        file_name = '{}_{}_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), self.user_data['user_id'],
                                      self.save_type)
        file_path = os.path.join(self.save_folder, '{}.npz'.format(file_name))

        self.depth_camera_worker.depth_camera.save_file(file_path)

        logging.info(f'[MAIN] save file: {file_name}')

        data = {
            'payload': {
                'user_id': self.user_data['user_id'],
                'weight': self.weight_reader_worker.weight_reader.val if self.is_weight_reader_ok else 0,
                'meal_date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'type': self.save_type
            },
            'file_path': file_path,
            'file_name': file_name
        }

        upload_worker = UploadWorker(base_url=self.config.get('api', 'base_url'), data=data)
        upload_worker.setAutoDelete(True)
        upload_worker.signals.result.connect(self.return_upload_result)

        self.thread_pool.start(upload_worker)

        self.save_json({
            file_name: {
                'user_id': self.user_data['user_id'],
                'weight': self.weight_reader_worker.weight_reader.val if self.is_weight_reader_ok else 0,
                'save_type': self.save_type,
                'is_upload': self.is_upload
            }
        })

        logging.info('[MAIN] save json')

        self.user_data = None
        self.save_type = None
        self.is_upload = 0

        self.change_page(UI_PAGE_NAME.MESSAGE)
        self.change_status(LED_STATUS.IDLE)

    def save_json(self, data):
        if os.path.isfile(self.json_path):
            with open(self.json_path) as json_file:
                json_data = json.load(json_file)
        else:
            json_data = {}

        json_data.update(data)

        with open(self.json_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=4)

    def return_upload_result(self, is_upload):
        self.is_upload = is_upload

    def change_page(self, page):
        self.main_window.return_button.hide()
        self.main_window.setting_button.hide()
        self.main_window.exit_button.hide()

        if page == UI_PAGE_NAME.USER_SELECT:
            self.set_title_text(
                f"{self.config.get('school', 'name')}{self.config.getint('school', 'grade')}年{self.config.get('school', 'class')}班")
            self.main_window.setting_button.show()
        elif page == UI_PAGE_NAME.USER_CONTROL:
            self.set_title_text(f"您好，{self.user_data['name']}同學")
            self.main_window.return_button.show()
        elif page == UI_PAGE_NAME.LOADING:
            pass
        elif page == UI_PAGE_NAME.MESSAGE:
            self.complete_message.start()
        elif page == UI_PAGE_NAME.SETTING:
            self.set_title_text('設定')
            self.main_window.return_button.show()
            self.main_window.exit_button.show()
        elif page == UI_PAGE_NAME.ERROR_MSG:
            self.main_window.return_button.show()
            self.main_window.exit_button.show()

        self.stacked_layout.setCurrentIndex(page)

    def user_button_handler(self, data):
        self.user_data = data
        self.change_page(UI_PAGE_NAME.USER_CONTROL)

    def show_image(self, img):
        len_y, len_x, _ = img.shape
        qimg = QImage(img.data, len_x, len_y, QImage.Format_RGB888)
        self.user_control.image_view.setPixmap(QPixmap.fromImage(qimg))

    def set_setting_page_options(self):
        self.change_status(LED_STATUS.BUSY)
        self.change_page(UI_PAGE_NAME.LOADING)

        worker = Worker(self.api.fetch_schools)
        worker.signals.result.connect(self.fetch_schools_handler)
        worker.setAutoDelete(True)
        self.thread_pool.start(worker)

    def fetch_schools_handler(self, res):
        status_code, schools = res
        if status_code == 200:
            self.setting_page.set_options(schools, self.config.items('school'))
            self.change_page(UI_PAGE_NAME.SETTING)
        else:
            self.change_page(UI_PAGE_NAME.ERROR_MSG)

        self.change_status(LED_STATUS.IDLE)

    def set_user_list(self):
        worker = Worker(
            self.api.fetch_user_list,
            school_id=self.config.getint('school', 'id'),
            grade=self.config.getint('school', 'grade'),
            class_name=self.config.getint('school', 'class')
        )
        worker.setAutoDelete(True)
        worker.signals.result.connect(self.fetch_user_list_handler)

        if self.status == LED_STATUS.IDLE:  # if status is not init
            self.change_status(LED_STATUS.BUSY)
            self.change_page(UI_PAGE_NAME.LOADING)
            worker.signals.finished.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        self.thread_pool.start(worker)

    def fetch_user_list_handler(self, res):
        status_code, user_list = res
        if status_code == 200:
            with open(USER_LIST_PATH, 'w', encoding='utf8') as outfile:
                json.dump(user_list, outfile, indent=4, ensure_ascii=False)
        elif os.path.isfile(USER_LIST_PATH):
            with open(USER_LIST_PATH) as json_file:
                user_list = json.load(json_file)

        self.user_select.set_user_btn_page(user_list)

        if self.status == LED_STATUS.BUSY:
            self.change_status(LED_STATUS.IDLE)

    def save_handler(self, data):
        self.save_config(data)
        self.set_user_list()

    def save_config(self, data):
        for section, value in data.items():
            for attr, val in value.items():
                self.config[section][attr] = str(val)

        with open(CONFIG_PATH, 'w', encoding='utf-8') as config_file:
            self.config.write(config_file)

        logging.info('[MAIN] save config')

    def exit_handler(self):
        self.timer.stop()
        self.depth_camera_worker.set_stop(True)
        self.depth_camera_worker.depth_camera.pipeline.stop()
        self.weight_reader_worker.set_stop(True)
        self.led_controller.clear_GPIO()

        self.close()
        logging.info('*** Close application ***')


if __name__ == '__main__':
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    DATE_FORMAT = '%Y%m%d %H:%M:%S'

    if args.show_log:
        log_file_path = None
        log_level = logging.DEBUG
    else:
        log_file_name = '{}_log.log'.format(datetime.datetime.now().strftime("%Y%m%d"))
        log_file_path = os.path.join('logs', log_file_name)
        os.makedirs('logs', exist_ok=True)
        log_level = logging.INFO

    logging.basicConfig(level=log_level, filename=log_file_path, filemode='a', format=FORMAT)
    logging.info(f'*** Start application {CODE_VERSION} ***')

    logging.info('[MAIN] read config file')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')

    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())
