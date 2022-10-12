import argparse
import datetime
import json
import os
import sys
import logging
import configparser

from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout

from ui.config import UI_PAGE_NAME
from ui.loading_component import LoadingComponent
from ui.main_page import Ui_MainWindow
from ui.message_component import MessageComponent
from ui.user_control import UserControl
from ui.user_select import UserSelect
from ui.setting_page import SettingPage

from utils.led import LedController
from utils.api import Api

from worker.camera_worker import DepthCameraWorker
from worker.weight_worker import WeightReaderWorker
from worker.upload_worker import UploadWorker

CODE_VERSION = '1.0.1'

CONFIG_PATH = r'config/config.ini'

parser = argparse.ArgumentParser()
parser.add_argument('-sl', '--show_log', action='store_true', help='show message in terminal')
args = parser.parse_args()

class MainWindow(QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.config = config
        self.api = Api(config.get('api', 'base_url'))

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
        self.main_window.button_setting_signal.connect(lambda: self.change_page(UI_PAGE_NAME.SETTING))

        self.showFullScreen()

        # user select page
        self.user_select = UserSelect()
        self.set_user_list()
        self.user_select.user_btn_click_signal.connect(self.user_button_handler)

        self.set_title_text(
            f"{self.config.get('school', 'name')}{self.config.getint('school', 'grade')}年{self.config.get('school', 'class')}班")

        # user control page
        self.user_control = UserControl()
        self.user_control.button_click_signal.connect(self.user_control_handler)

        # loading component
        self.loading_component = LoadingComponent()

        # message component
        self.message_component = MessageComponent()
        self.message_component.close_signal.connect(lambda: self.change_page(UI_PAGE_NAME.USER_SELECT))

        # setting page
        self.setting_page = SettingPage()
        self.setting_page.save_signal.connect(self.save_handler)

        # stack layout
        self.qls = QStackedLayout()
        self.qls.addWidget(self.user_select)
        self.qls.addWidget(self.user_control)
        self.qls.addWidget(self.loading_component)
        self.qls.addWidget(self.message_component)
        self.qls.addWidget(self.setting_page)

        self.main_window.verticalLayout.addLayout(self.qls)

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
        self.is_upload = 0

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

        file_name = '{}_{}_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), self.user_data['user_id'],
                                      self.save_type)
        file_path = os.path.join(self.save_folder, '{}.npz'.format(file_name))

        self.depth_camera_worker.depth_camera.save_file(file_path)

        logging.info(f'[MAIN] save file: {file_name}')

        data = {
            'payload': {
                'user_id': self.user_data['user_id'],
                'weight': self.weight_reader_worker.weight_reader.val,
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
                'weight': self.weight_reader_worker.weight_reader.val,
                'save_type': self.save_type,
                'is_upload': self.is_upload
            }
        })

        logging.info('[MAIN] save json')

        self.user_data = None
        self.save_type = None
        self.is_upload = 0

        self.change_page(UI_PAGE_NAME.MESSAGE)

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

    def return_upload_result(self, is_upload):
        self.is_upload = is_upload

    def change_page(self, page):
        self.main_window.return_button.hide()
        self.main_window.setting_button.hide()

        if page == UI_PAGE_NAME.USER_SELECT:
            self.set_title_text(
                f"{self.config.get('school', 'name')}{self.config.getint('school', 'grade')}年{self.config.get('school', 'class')}班")
            self.main_window.setting_button.show()
        elif page == UI_PAGE_NAME.USER_CONTROL:
            self.set_title_text(f"您好，{self.user_data['name']}同學")
            self.main_window.return_button.show()
        elif page == UI_PAGE_NAME.LOADING:
            self.loading_component.start()
        elif page == UI_PAGE_NAME.MESSAGE:
            self.message_component.start()
        elif page == UI_PAGE_NAME.SETTING:
            self.setting_page.set_options(self.api.fetch_schools(), self.config.items('school'))
            self.set_title_text('設定')
            self.main_window.return_button.show()

        self.qls.setCurrentIndex(page)

    def user_button_handler(self, data):
        self.user_data = data
        self.change_page(UI_PAGE_NAME.USER_CONTROL)

    def show_image(self, img):
        len_y, len_x, _ = img.shape
        qimg = QImage(img.data, len_x, len_y, QImage.Format_RGB888)
        self.user_control.image_view.setPixmap(QPixmap.fromImage(qimg))

    def set_user_list(self):
        status_code, user_list = self.api.fetch_user_list(
            school_id=self.config.getint('school', 'id'),
            grade=self.config.getint('school', 'grade'),
            class_name=self.config.getint('school', 'class')
        )
        
        if status_code == 200:
            with open(r'config/user_list.json', 'w', encoding='utf8') as outfile:
                json.dump(user_list, outfile, indent=4, ensure_ascii=False)
        elif os.path.isfile(r'config/user_list.json'):
            with open(r'config/user_list.json') as json_file:
                user_list = json.load(json_file)

        self.user_select.set_user_btn_page(user_list)
    
    def save_handler(self, data):
        self.save_config(data)
        self.set_user_list()
        self.change_page(UI_PAGE_NAME.USER_SELECT)
        
    def save_config(self, data):
        for section, value in data.items():
            for attr, val in value.items():
                self.config[section][attr] = str(val)

        with open(CONFIG_PATH, 'w', encoding='utf-8') as config_file:
            self.config.write(config_file)

        logging.info('[MAIN] save config')

    def exit_handler(self):
        self.led_controller.clear_GPIO()
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
