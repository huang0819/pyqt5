from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QComboBox, QSpinBox
from PyQt5.QtCore import pyqtSignal


class COLOR_MAP:
    GREEN = {
        'common_color': '#548235',
        'pressed_color': '#A9D18E'
    }
    BLUE = {
        'common_color': '#2E75B6',
        'pressed_color': '#9DC3E6'
    }


BTN_STYLE = """
    QPushButton {{
        background-color: {common_color};
        color: #FFFFFF;
        border-style: outset;
        padding: 2px;
        font: 58px 微軟正黑體;
        border-width: 1px;
        border-radius: 10px;
        border-color: transparent;
    }}
    QPushButton:pressed {{
        background-color: {pressed_color};
    }}"""


class Label(QLabel):
    FONT = QtGui.QFont('微軟正黑體', 36)

    def __init__(self, parent, text, start):
        super(Label, self).__init__()

        self.setParent(parent)
        self.setText(text)
        self.setFont(self.FONT)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        self.resize(self.sizeHint())
        self.setFixedHeight(100)

        self.setGeometry(QtCore.QRect(start[0], start[1], self.width(), self.height()))


class Select(QComboBox):
    data_signal = pyqtSignal(object)
    FONT = QtGui.QFont('微軟正黑體', 36)

    def __init__(self, parent, start, size):
        super(Select, self).__init__()

        self.setParent(parent)
        self.setFont(self.FONT)
        self.setStyleSheet("""
                    QComboBox {
                        background-color: #f0f0f0;
                        border: 3px solid #8c8c8c;
                        padding: 0 20px 0 20px
                    }
                    QComboBox::drop-down {
                        width: 60px;
                    }
                    """)
        self.resize(*size)
        self.setGeometry(QtCore.QRect(*start, self.width(), self.height()))

        self.currentIndexChanged.connect(self.handler)

        self.options = []

    def set_options(self, options, label, current_label):
        self.options = options

        if label is not None:
            label_options = [x[label] for x in self.options]
        else:
            label_options = options

        self.addItems(label_options)
        current_index = label_options.index(current_label)

        self.setCurrentIndex(current_index)

    def handler(self, index):
        self.data_signal.emit(self.options[index])

class ClassSelect(QSpinBox):
    data_signal = pyqtSignal(object)
    FONT = QtGui.QFont('微軟正黑體', 36)

    def __init__(self, parent, start, size):
        super(ClassSelect, self).__init__()

        self.setParent(parent)
        self.setFont(self.FONT)
        self.setStyleSheet("""
                    QSpinBox {
                        background-color: #f0f0f0;
                        border: 3px solid #8c8c8c;
                        padding: 0 20px 0 20px
                    }
                    QSpinBox::drop-down {
                        width: 30px;
                    }
                    """)
        self.resize(*size)
        self.setGeometry(QtCore.QRect(*start, self.width(), self.height()))

        self.valueChanged.connect(self.handler)

        self.setRange(1, 20)
        self.setSuffix('班')

    def set_options(self, current_label):
        self.setValue(current_label)

    def handler(self, value):
        self.data_signal.emit(value)


class SettingPage(QWidget):
    ICON_SIZE = 64

    FONT = QtGui.QFont('微軟正黑體', 36)

    save_signal = pyqtSignal(dict)

    def __init__(self, **kwargs):
        super(SettingPage, self).__init__()

        self.school_data = None
        self.grade = None
        self.class_name = None

        # 1880 * 1040
        self.setGeometry(0, 0, 1880, 900)

        self.label_school = Label(self, '學校', (100, 100))
        self.select_school = Select(self, (300, 100), (1000, 100))
        self.select_school.data_signal.connect(self.set_school_data)

        self.label_grade = Label(self, '年級', (100, 300))
        self.select_grade = Select(self, (300, 300), (1000, 100))
        self.select_grade.data_signal.connect(self.set_grade)

        self.label_class = Label(self, '班級', (100, 500))
        self.select_class = ClassSelect(self, (300, 500), (1000, 100))
        self.select_class.data_signal.connect(self.set_class)

        # set save btn
        self.save_btn = QPushButton('儲存', self)
        self.save_btn.setMaximumSize(200, 100)
        self.save_btn.setStyleSheet(BTN_STYLE.format(**COLOR_MAP.BLUE))
        self.save_btn.clicked.connect(self.save_setting)
        self.save_btn.setGeometry(840, 700, 200, 100)

        self.schools = []

    def save_setting(self):
        self.save_signal.emit({
            'school': {
                'id': self.school_data['id'],
                'name': self.school_data['name'],
                'grade': self.grade['value'],
                'class': self.class_name
            }
        })

        self.clear()

    def clear(self):
        self.select_school.clear()
        self.select_grade.clear()
        self.select_class.clear()

        self.school_data = None
        self.grade = None
        self.class_name = None

    def set_options(self, schools, school_config):
        self.clear()

        current = dict(school_config)
        self.school_data = {'id': current['id'], 'name': current['name']}
        self.grade = {'value': current['grade']}
        self.class_name = current['class']

        self.select_school.set_options(schools, 'name', current['name'])

        grades = []
        for i in range(1, 10):
            grades.append({
                'label': f'{i}年級',
                'value': i
            })

        self.select_grade.set_options(grades, 'label', f"{current['grade']}年級")

        self.select_class.set_options(int(current['class']))

    def set_school_data(self, data):
        self.school_data = data

    def set_grade(self, data):
        self.grade = data

    def set_class(self, data):
        self.class_name = data
