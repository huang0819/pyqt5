from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QStackedLayout, QLabel
from ui.user_button import UserButton

class UserSelect(QWidget):
    BTN_SIZE = 150
    FONT_STYLE = QtGui.QFont('微軟正黑體', 28)
    FONT_STYLE_SHEET = 'color: #ff970c; font-weight: bold;'
    PREVIOUS = -1
    NEXT = 1

    user_btn_click_signal = pyqtSignal(object)

    def __init__(self, **kwargs):
        super(UserSelect, self).__init__()
        self.kwargs = kwargs

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 1040)

        # previous btn
        self.previous_button = QPushButton('', self)
        self.previous_button.setMaximumSize(self.BTN_SIZE, self.BTN_SIZE)
        self.previous_button.setIcon(QtGui.QIcon(r'resource/previous.png'))
        self.previous_button.setIconSize(QtCore.QSize(self.BTN_SIZE, self.BTN_SIZE))
        self.previous_button.setStyleSheet('background-color: #f0f0f0; border: none')
        self.previous_button.setGeometry(
            QtCore.QRect(0, self.height() // 2 - self.BTN_SIZE - 30, self.BTN_SIZE, self.BTN_SIZE))
        self.previous_button.clicked.connect(lambda: self.page_btn_handler(self.PREVIOUS))

        # previous label
        self.previous_label = QLabel('上一頁', self)
        self.previous_label.setFont(self.FONT_STYLE)
        self.previous_label.setStyleSheet(self.FONT_STYLE_SHEET)
        self.previous_label.setAlignment(QtCore.Qt.AlignLeft)
        self.previous_label.resize(self.previous_label.sizeHint())
        self.previous_label.setGeometry(
            QtCore.QRect(0, self.height() // 2 - 20, self.BTN_SIZE, self.BTN_SIZE))

        # next btn
        self.next_button = QPushButton('', self)
        self.next_button.setMaximumSize(self.BTN_SIZE, self.BTN_SIZE)
        self.next_button.setIcon(QtGui.QIcon(r'resource/next.png'))
        self.next_button.setIconSize(QtCore.QSize(self.BTN_SIZE, self.BTN_SIZE))
        self.next_button.setStyleSheet('background-color: #f0f0f0; border: none')
        self.next_button.setGeometry(
            QtCore.QRect(self.width() - self.BTN_SIZE, self.height() // 2 - self.BTN_SIZE - 30, self.BTN_SIZE,
                         self.BTN_SIZE))
        self.next_button.clicked.connect(lambda: self.page_btn_handler(self.NEXT))

        # next label
        self.next_label = QLabel('下一頁', self)
        self.next_label.setFont(self.FONT_STYLE)
        self.next_label.setStyleSheet(self.FONT_STYLE_SHEET)
        self.next_label.setAlignment(QtCore.Qt.AlignLeft)
        self.next_label.resize(self.previous_label.sizeHint())
        self.next_label.setGeometry(
            QtCore.QRect(self.width() - self.BTN_SIZE, self.height() // 2 - 20, self.BTN_SIZE, self.BTN_SIZE))

        # user_btn_area
        self.user_btn_area = QWidget(self)
        self.user_btn_area.setGeometry(self.BTN_SIZE, 0, self.width() - self.BTN_SIZE * 2, 900)

        self.stacked_layout = QStackedLayout()
        self.user_btn_area.setLayout(self.stacked_layout)

        self.user_btn_pages = []
        self.user_buttons = []

        # params
        self.max_page = 0
        self.page = 0

    def set_user_btn_page(self, user_list):
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

    def __init__(self, **kwargs):
        super(UserBtnPage, self).__init__()

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(50)
        self.grid_layout.setGeometry(QtCore.QRect(0, 0, 1680, 840))

        self.setLayout(self.grid_layout)

        self.user_buttons = []

    def set_user_btn(self, user_list):
        self.user_buttons = []

        for index, user_data in enumerate(user_list):
            self.user_buttons.append(UserButton(data=user_data, index=index))
            self.user_buttons[index].resize(self.user_buttons[index].sizeHint())
            self.user_buttons[index].user_click_signal.connect(self.user_btn_handler)

            self.grid_layout.addWidget(self.user_buttons[index], index // 5, index % 5, 1, 1)

    def user_btn_handler(self, data):
        self.user_btn_click_signal.emit(data)
