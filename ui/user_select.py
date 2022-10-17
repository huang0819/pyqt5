from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QStackedLayout, QLabel
from ui.user_button import UserButton


class PageButton(QWidget):
    BTN_SIZE = 150

    def __init__(self, parent, start, button_type):
        super(PageButton, self).__init__()

        assert button_type in ['previous', 'next'], 'button type must be "previous" or "next"'

        self.setParent(parent)

        # button
        self.button = QPushButton('', self)
        self.button.resize(self.BTN_SIZE, self.BTN_SIZE)
        self.button.setStyleSheet("""
            QPushButton{{
                background-color: transparent; 
                border: none; 
                image: url(resource/{button_type}.png)
            }}
            QPushButton:pressed {{
                background-color: transparent; 
                border: none; 
                image: url(resource/{button_type}_pressed.png)
            }}
        """.format(button_type=button_type))
        self.button.setGeometry(QtCore.QRect(*start, self.BTN_SIZE, self.BTN_SIZE))

        # label
        self.label = QLabel('上一頁' if button_type == 'previous' else '下一頁', self)
        self.label.setFont(QtGui.QFont('微軟正黑體', 28))
        self.label.setStyleSheet('color: #ff970c; font-weight: bold;')
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.resize(self.label.sizeHint())
        self.label.setGeometry(QtCore.QRect(start[0], start[1] + self.BTN_SIZE + 10, self.BTN_SIZE, self.BTN_SIZE))


class UserSelect(QWidget):
    BTN_SIZE = 150
    PREVIOUS = -1
    NEXT = 1

    user_btn_click_signal = pyqtSignal(object)

    def __init__(self):
        super(UserSelect, self).__init__()

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 1040)

        # next btn
        self.next_button = PageButton(self, (self.width() - self.BTN_SIZE, self.height() // 2 - self.BTN_SIZE - 30), 'next')
        self.next_button.button.clicked.connect(lambda: self.page_btn_handler(self.NEXT))

        # previous btn
        self.previous_button = PageButton(self, (0, self.height() // 2 - self.BTN_SIZE - 30), 'previous')
        self.previous_button.button.clicked.connect(lambda: self.page_btn_handler(self.PREVIOUS))

        # user_btn_area
        self.user_btn_area = QWidget(self)
        self.user_btn_area.setGeometry(self.BTN_SIZE, 0, self.width() - self.BTN_SIZE * 2, 900)

        self.stacked_layout = QStackedLayout()
        self.user_btn_area.setLayout(self.stacked_layout)

        self.user_btn_pages = []

        # params
        self.max_page = 0
        self.page = 0

    def set_user_btn_page(self, user_list):
        for user_btn_page in self.user_btn_pages:
            self.stacked_layout.removeWidget(user_btn_page)

        self.user_btn_pages = []

        self.page = 0
        self.max_page = len(user_list) // 10

        for page, start_index in enumerate(range(0, len(user_list), 10)):
            self.user_btn_pages.append(UserBtnPage())
            self.user_btn_pages[page].set_user_btn(user_list[start_index: start_index + 10])
            self.user_btn_pages[page].user_btn_click_signal.connect(self.user_btn_handler)

            self.stacked_layout.addWidget(self.user_btn_pages[page])

        self.stacked_layout.setCurrentIndex(0)

    def user_btn_handler(self, data):
        self.user_btn_click_signal.emit(data)

    def page_btn_handler(self, direction):
        self.page += direction

        if self.page > self.max_page:
            self.page = 0
        elif self.page < 0:
            self.page = self.max_page

        self.stacked_layout.setCurrentIndex(self.page)


class UserBtnPage(QWidget):
    user_btn_click_signal = pyqtSignal(object)

    def __init__(self):
        super(UserBtnPage, self).__init__()
        self.user_buttons = []

    def set_user_btn(self, user_list):
        self.user_buttons = []

        for index, user_data in enumerate(user_list):
            self.user_buttons.append(UserButton(self, data=user_data, index=index))
            self.user_buttons[index].resize(self.user_buttons[index].sizeHint())
            self.user_buttons[index].user_click_signal.connect(self.user_btn_handler)
            self.user_buttons[index].setGeometry(QtCore.QRect(300 * (index % 5) + 20 * (index % 5), 30 + 440 * (index // 5), 300, 400))

    def user_btn_handler(self, data):
        self.user_btn_click_signal.emit(data)
