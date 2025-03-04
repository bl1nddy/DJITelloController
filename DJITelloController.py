import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer
from djitellopy import Tello

class TelloApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tello = Tello()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Загрузка классификатора Хаара для распознавания лиц
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Установка начальной темы
        self.current_theme = 'light'
        self.set_light_theme()

    def initUI(self):
        self.setWindowTitle('Управление дроном Tello')
        self.setGeometry(100, 100, 800, 600)

        # Установка иконки приложения
        self.setWindowIcon(QIcon('E:/Downloads/00002-800x600-Photoroom (1).png'))  # Укажите путь к вашему файлу иконки

        self.layout = QVBoxLayout()

        self.video_label = QLabel('Видеопоток')
        self.layout.addWidget(self.video_label)

        info_layout = QVBoxLayout()
        self.temp_label = QLabel('Температура: ')
        info_layout.addWidget(self.temp_label)

        self.pitch_label = QLabel('Угол наклона: ')
        info_layout.addWidget(self.pitch_label)

        self.barometer_label = QLabel('Барометр: ')
        info_layout.addWidget(self.barometer_label)

        self.distance_label = QLabel('Расстояние от старта: ')
        info_layout.addWidget(self.distance_label)

        self.battery_label = QLabel('Батарея: ')
        info_layout.addWidget(self.battery_label)

        self.altitude_label = QLabel('Высота: ')
        info_layout.addWidget(self.altitude_label)

        self.layout.addLayout(info_layout)

        self.movement_layout = QGridLayout()

        # Установка фиксированного размера для всех кнопок
        button_size = (150, 50)

        self.up_button = QPushButton('Вверх')
        self.up_button.setFixedSize(*button_size)
        self.up_button.clicked.connect(self.move_up)
        self.movement_layout.addWidget(self.up_button, 0, 1)

        self.left_button = QPushButton('Влево')
        self.left_button.setFixedSize(*button_size)
        self.left_button.clicked.connect(self.move_left)
        self.movement_layout.addWidget(self.left_button, 1, 0)

        self.forward_button = QPushButton('Вперед')
        self.forward_button.setFixedSize(*button_size)
        self.forward_button.clicked.connect(self.move_forward)
        self.movement_layout.addWidget(self.forward_button, 1, 1)

        self.right_button = QPushButton('Вправо')
        self.right_button.setFixedSize(*button_size)
        self.right_button.clicked.connect(self.move_right)
        self.movement_layout.addWidget(self.right_button, 1, 2)

        self.back_button = QPushButton('Назад')
        self.back_button.setFixedSize(*button_size)
        self.back_button.clicked.connect(self.move_back)
        self.movement_layout.addWidget(self.back_button, 2, 1)

        self.down_button = QPushButton('Вниз')
        self.down_button.setFixedSize(*button_size)
        self.down_button.clicked.connect(self.move_down)
        self.movement_layout.addWidget(self.down_button, 0, 2)

        self.layout.addLayout(self.movement_layout)

        control_layout = QHBoxLayout()

        self.connect_button = QPushButton('Подключиться')
        self.connect_button.setFixedSize(*button_size)
        self.connect_button.clicked.connect(self.connect_to_tello)
        control_layout.addWidget(self.connect_button)

        self.takeoff_button = QPushButton('Взлет')
        self.takeoff_button.setFixedSize(*button_size)
        self.takeoff_button.clicked.connect(self.takeoff)
        control_layout.addWidget(self.takeoff_button)

        self.land_button = QPushButton('Посадка')
        self.land_button.setFixedSize(*button_size)
        self.land_button.clicked.connect(self.land)
        control_layout.addWidget(self.land_button)

        self.emergency_stop_button = QPushButton('Экстренная пос.')
        self.emergency_stop_button.setFixedSize(*button_size)
        self.emergency_stop_button.clicked.connect(self.emergency_stop)
        control_layout.addWidget(self.emergency_stop_button)

        self.theme_button = QPushButton('Сменить тему')
        self.theme_button.setFixedSize(*button_size)
        self.theme_button.clicked.connect(self.switch_theme)
        control_layout.addWidget(self.theme_button)

        self.layout.addLayout(control_layout)

        self.setLayout(self.layout)

    def connect_to_tello(self):
        try:
            self.tello.connect()
            self.tello.streamon()
            self.timer.start(20)
            self.temp_label.setText('Подключено к Tello')
        except Exception as e:
            self.temp_label.setText(f'Ошибка подключения к Tello: {str(e)}')

    def update_frame(self):
        frame = self.tello.get_frame_read().frame
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Преобразуем в оттенки серого для распознавания лиц
            gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)

            # Обнаруживаем лица
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # Определяем цвет обводки в зависимости от темы
            if self.current_theme == 'light':
                color = (0, 0, 0)  # Черный цвет для светлой темы
            elif self.current_theme == 'dark':
                color = (255, 0, 0)  # Красный цвет для темной темы
            else:  # Фиолетовая тема
                color = (255, 255, 0)  # Желтый цвет для фиолетовой темы

            # Обводим лица
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), color, 2)  
                cv2.putText(frame_rgb, 'Лицо', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

            # Обновляем информацию о состоянии дрона
            self.update_sensor_data()

    def update_sensor_data(self):
        self.get_pitch()
        self.get_barometer()
        self.get_distance()
        self.get_battery()
        self.get_altitude()

    def get_pitch(self):
        pitch = self.tello.get_pitch()
        self.pitch_label.setText(f'Угол наклона: {pitch}')

    def get_barometer(self):
        barometer = self.tello.get_barometer()
        self.barometer_label.setText(f'Барометр: {barometer}')

    def get_distance(self):
        distance = self.tello.get_distance_tof()
        self.distance_label.setText(f'Расстояние от старта: {distance} м')

    def get_battery(self):
        battery = self.tello.get_battery()
        self.battery_label.setText(f'Батарея: {battery}%')

    def get_altitude(self):
        altitude = self.tello.get_height()
        self.altitude_label.setText(f'Высота: {altitude} см')

    def takeoff(self):
        self.tello.takeoff()
        self.temp_label.setText('Дрон взлетел')

    def land(self):
        self.tello.land()
        self.temp_label.setText('Дрон приземляется')

    def emergency_stop(self):
        self.tello.land()
        self.temp_label.setText('Экстренная посадка активирована')

    def move_forward(self):
        self.tello.move_forward(30)
        self.temp_label.setText('Движение вперед')

    def move_back(self):
        self.tello.move_back(30)
        self.temp_label.setText('Движение назад')

    def move_left(self):
        self.tello.move_left(30)
        self.temp_label.setText('Движение влево')

    def move_right(self):
        self.tello.move_right(30)
        self.temp_label.setText('Движение вправо')

    def move_up(self):
        self.tello.move_up(30)
        self.temp_label.setText('Движение вверх')

    def move_down(self):
        self.tello.move_down(30)
        self.temp_label.setText('Движение вниз')

    def closeEvent(self, event):
        self.tello.end()
        event.accept()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #cfcfcf;
            }
            QWidget {
                background-color: #494949;  /* Цвет фона для темной темы */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3c3c3c;  /* Цвет фона кнопок для темной темы */
                color: #cfcfcf;              /* Цвет текста кнопок для темной темы */
                border: none;                /* Убираем рамку */
                padding: 10px;               /* Отступы внутри кнопок */
                border-radius: 5px;          /* Закругление углов кнопок */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;   /* Цвет кнопки при наведении для темной темы (темнее) */
            }
        """)

    def set_purple_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #351c75;
            }
            QWidget {
                background-color: #8e7cc3;  /* Цвет фона для фиолетовой темы */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #b4a7d6;  /* Цвет фона кнопок для фиолетовой темы */
                color: #351c75;              /* Цвет текста кнопок для фиолетовой темы */
                border: none;                /* Убираем рамку */
                padding: 10px;               /* Отступы внутри кнопок */
                border-radius: 5px;          /* Закругление углов кнопок */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7768a4;   /* Цвет кнопки при наведении для фиолетовой темы */
            }
        """)

    def set_light_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #2b2b2b;
            }
            QWidget {
                background-color: #ececec;  /* Цвет фона для светлой темы */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #e2e2e2;  /* Цвет фона кнопок для светлой темы */
                color: #2b2b2b;              /* Цвет текста кнопок для светлой темы */
                border: none;                /* Убираем рамку */
                padding: 10px;               /* Отступы внутри кнопок */
                border-radius: 5px;          /* Закругление углов кнопок */
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d5d5d5;   /* Цвет кнопки при наведении для светлой темы */
            }
        """)

    def switch_theme(self):
        if self.current_theme == 'light':
            self.set_dark_theme()
            self.current_theme = 'dark'
            self.theme_button.setText('Фиолетовая тема')
        elif self.current_theme == 'dark':
            self.set_purple_theme()
            self.current_theme = 'purple'
            self.theme_button.setText('Светлая тема')
        else:
            self.set_light_theme()
            self.current_theme = 'light'
            self.theme_button.setText('Темная тема')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TelloApp()
    ex.show()
    sys.exit(app.exec_())
