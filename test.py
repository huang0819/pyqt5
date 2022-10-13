import argparse
import datetime
import os
import sys
import logging
import configparser

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedLayout

from ui.config import UI_PAGE_NAME
from ui.main_page import Ui_MainWindow
from ui.message_component import MessageComponent
from ui.test_module_page import TestModulePage


CODE_VERSION = '1.0.1'

CONFIG_PATH = r'config/config.ini'

parser = argparse.ArgumentParser()
parser.add_argument('-sl', '--show_log', action='store_true', help='show message in terminal')
args = parser.parse_args()


class MainWindow(QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.config = config

        # ui setup
        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.main_window.exit_button.show()
        self.main_window.button_exit_signal.connect(self.exit_handler)

        self.showFullScreen()

        self.test_module_page = TestModulePage(self.config)
        self.test_module_page.save_config_signal.connect(self.save_config)
        self.test_module_page.init_finish_signal.connect(lambda: self.qls.setCurrentIndex(1))

        # init message component
        self.init_message_component = MessageComponent(text='初始化中，請稍候。', font_size=64, color='#2E75B6', wait_time=0)

        self.set_title_text(f"測試裝置")

        # stack layout
        self.qls = QStackedLayout()
        self.qls.addWidget(self.init_message_component)
        self.qls.addWidget(self.test_module_page)
        
        self.main_window.verticalLayout.addLayout(self.qls)

    def set_title_text(self, text):
        self.main_window.title.setText(text)

    def save_config(self, data):
        for section, value in data.items():
            for attr, val in value.items():
                self.config[section][attr] = str(val)

        with open(CONFIG_PATH, 'w', encoding='utf-8') as config_file:
            self.config.write(config_file)

        logging.info('[MAIN] save config')

    def exit_handler(self):
        self.test_module_page.exit_handler()
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
    logging.info(f'*** Start test module {CODE_VERSION} ***')

    logging.info('[MAIN] read config file')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')

    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())
