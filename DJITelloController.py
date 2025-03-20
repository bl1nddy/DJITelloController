import sys
import cv2
import numpy as np
import mediapipe as mp
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

        # Загрузка распознавания лиц
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Инициализация MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        # Установка начальной темы
        self.current_theme = 'light'
        self.set_light_theme()

    def initUI(self):
        self.setWindowTitle('Управление дроном Tello')
        self.setGeometry(100, 100, 800, 600)

        # Установка иконки приложения
        self.setWindowIcon(QIcon('Иконка.png')) 

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
            self.timer.start(10)  # Установите интервал на 10 мс для увеличения FPS
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

            # Определяем цвет для обводки лиц
            color = (255, 255, 255)  # Белый цвет в формате BGR

            # Обработка жестов рук
            results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame_rgb, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # Определяем жесты
                    thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
                    pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]

                    # Проверка на ладонь (открытая рука)
                    if thumb_tip.y < index_tip.y and thumb_tip.y < middle_tip.y:
                        self.land() 
                        self.temp_label.setText('Ладонь обнаружена: Дрон садится')
                        break

                    # Проверка на кулак (сжатая рука)
                    if thumb_tip.y > index_tip.y and thumb_tip.y > middle_tip.y:
                        try:
                            self.tello.rotate_clockwise(90) 
                            self.temp_label.setText('Кулак обнаружен: Дрон поворачивается на 90 градусов')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при повороте: {str(e)}')
                        break

                    # Проверка на жест "указательный палец вверх"
                    if (index_tip.y < thumb_tip.y and
                        middle_tip.y > thumb_tip.y and
                        ring_tip.y > thumb_tip.y and
                        pinky_tip.y > thumb_tip.y):
                        try:
                            self.tello.move_up(20) 
                            self.temp_label.setText('Указательный палец вверх обнаружен: Дрон летит вверх на 20 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении вверх: {str(e)}')
                        break

                    # Проверка на жест "указательный палец вниз"
                    if (index_tip.y > thumb_tip.y and
                        middle_tip.y < thumb_tip.y and
                        ring_tip.y > thumb_tip.y and
                        pinky_tip.y > thumb_tip.y):
                        try:
                            self.tello.move_down(20)
                            self.temp_label.setText('Указательный палец вниз обнаружен: Дрон летит вниз на 20 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении вниз: {str(e)}')
                        break

                    # Проверка на жест "движение вперед"
                    if (index_tip.y < thumb_tip.y and
                        middle_tip.y < thumb_tip.y and
                        ring_tip.y > thumb_tip.y and
                        pinky_tip.y > thumb_tip.y):
                        try:
                            self.tello.move_forward(30)
                            self.temp_label.setText('Движение вперед обнаружено: Дрон движется вперед на 30 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении вперед: {str(e)}')
                        break

                    # Проверка на жест "движение назад"
                    if (index_tip.y > thumb_tip.y and
                        middle_tip.y > thumb_tip.y and
                        ring_tip.y < thumb_tip.y and
                        pinky_tip.y < thumb_tip.y):
                        try:
                            self.tello.move_back(30)
                            self.temp_label.setText('Движение назад обнаружено: Дрон движется назад на 30 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении назад: {str(e)}')
                        break

                    # Проверка на жест "движение влево"
                    if (index_tip.x < thumb_tip.x and
                        middle_tip.x < thumb_tip.x and
                        ring_tip.x > thumb_tip.x and
                        pinky_tip.x > thumb_tip.x):
                        try:
                            self.tello.move_left(30)
                            self.temp_label.setText('Движение влево обнаружено: Дрон движется влево на 30 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении влево: {str(e)}')
                        break

                    # Проверка на жест "движение вправо"
                    if (index_tip.x > thumb_tip.x and
                        middle_tip.x > thumb_tip.x and
                        ring_tip.x < thumb_tip.x and
                        pinky_tip.x < thumb_tip.x):
                        try:
                            self.tello.move_right(30)
                            self.temp_label.setText('Движение вправо обнаружено: Дрон движется вправо на 30 см')
                        except Exception as e:
                            self.temp_label.setText(f'Ошибка при движении вправо: {str(e)}')
                        break

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
        try:
            self.tello.takeoff()
            self.temp_label.setText('Дрон взлетел')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при взлете: {str(e)}')

    def land(self):
        try:
            self.tello.land()
            self.temp_label.setText('Дрон приземляется')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при посадке: {str(e)}')

    def emergency_stop(self):
        try:
            self.tello.land()
            self.temp_label.setText('Экстренная посадка активирована')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при экстренной посадке: {str(e)}')

    def move_forward(self):
        try:
            self.tello.move_forward(30)
            self.temp_label.setText('Движение вперед')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении вперед: {str(e)}')

    def move_back(self):
        try:
            self.tello.move_back(30)
            self.temp_label.setText('Движение назад')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении назад: {str(e)}')

    def move_left(self):
        try:
            self.tello.move_left(30)
            self.temp_label.setText('Движение влево')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении влево: {str(e)}')

    def move_right(self):
        try:
            self.tello.move_right(30)
            self.temp_label.setText('Движение вправо')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении вправо: {str(e)}')

    def move_up(self):
        try:
            self.tello.move_up(30)
            self.temp_label.setText('Движение вверх')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении вверх: {str(e)}')

    def move_down(self):
        try:
            self.tello.move_down(30)
            self.temp_label.setText('Движение вниз')
        except Exception as e:
            self.temp_label.setText(f'Ошибка при движении вниз: {str(e)}')

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
