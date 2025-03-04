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

    def initUI(self):
        self.setWindowTitle('Tello Drone Control')
        self.resize(800, 600)  # Устанавливаем начальный размер окна, но не фиксируем его

        self.setWindowIcon(QIcon('E:/Downloads/00002-800x600-Photoroom (1).png'))

        self.layout = QVBoxLayout()

        # Заголовок для видео
        self.title_label = QLabel('Live Translation')
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Создаем метку для видео
        self.video_label = QLabel('Video Feed')
        self.video_label.setMinimumSize(640, 480)  # Устанавливаем минимальный размер для видео
        self.layout.addWidget(self.video_label)

        # Создаем вертикальный layout для информации
        info_layout = QVBoxLayout()
        self.temp_label = QLabel('Temperature: ')
        info_layout.addWidget(self.temp_label)

        self.pitch_label = QLabel('Pitch: ')
        info_layout.addWidget(self.pitch_label)

        self.barometer_label = QLabel('Barometer: ')
        info_layout.addWidget(self.barometer_label)

        self.distance_label = QLabel('Distance from Start: ')
        info_layout.addWidget(self.distance_label)

        self.battery_label = QLabel('Battery: ')
        info_layout.addWidget(self.battery_label)

        self.altitude_label = QLabel('Altitude: ')
        info_layout.addWidget(self.altitude_label)

        # Добавляем информацию в основной layout
        self.layout.addLayout(info_layout)

        self.movement_layout = QGridLayout()

        self.up_button = QPushButton('Move Up')
        self.up_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.up_button.clicked.connect(self.move_up)
        self.movement_layout.addWidget(self.up_button, 0, 1)

        self.left_button = QPushButton('Move Left')
        self.left_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_button.clicked.connect(self.move_left)
        self.movement_layout.addWidget(self.left_button, 1, 0)

        self.forward_button = QPushButton('Move Forward')
        self.forward_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.forward_button.clicked.connect(self.move_forward)
        self.movement_layout.addWidget(self.forward_button, 1, 1)

        self.right_button = QPushButton('Move Right')
        self.right_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_button.clicked.connect(self.move_right)
        self.movement_layout.addWidget(self.right_button, 1, 2)

        self.back_button = QPushButton('Move Back')
        self.back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.back_button.clicked.connect(self.move_back)
        self.movement_layout.addWidget(self.back_button, 2, 1)

        self.down_button = QPushButton('Move Down')
        self.down_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.down_button.clicked.connect(self.move_down)
        self.movement_layout.addWidget(self.down_button, 0, 2)

        self.layout.addLayout(self.movement_layout)

        control_layout = QHBoxLayout()

        self.connect_button = QPushButton('Connect to Tello')
        self.connect_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.connect_button.clicked.connect(self.connect_to_tello)
        control_layout.addWidget(self.connect_button)

        self.takeoff_button = QPushButton('Takeoff')
        self.takeoff_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.takeoff_button.clicked.connect(self.takeoff)
        control_layout.addWidget(self.takeoff_button)

        self.land_button = QPushButton('Land')
        self.land_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.land_button.clicked.connect(self.land)
        control_layout.addWidget(self.land_button)

        self.emergency_stop_button = QPushButton('Emergency Stop')
        self.emergency_stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.emergency_stop_button.clicked.connect(self.emergency_stop)
        control_layout.addWidget(self.emergency_stop_button)

        self.theme_button = QPushButton('Dark Theme')
        self.theme_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.theme_button.clicked.connect(self.switch_theme)
        control_layout.addWidget(self.theme_button)

        self.layout.addLayout(control_layout)

        self.setLayout(self.layout)
        self.current_theme = 'light'
        self.set_light_theme()

    def connect_to_tello(self):
        try:
            self.tello.connect()
            self.tello.streamon()
            self.temp_label.setText('Connected to Tello')
            self.timer.start(20)
        except Exception as e:
            self.temp_label.setText(f'Error: {str(e)}')

    def update_frame(self):
        frame = self.tello.get_frame_read().frame
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Преобразуем в оттенки серого
            gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)

            # Обнаруживаем лица
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # Обводим лица
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)  
                cv2.putText(frame_rgb, 'Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

            # Обновляем информацию о состоянии дрона
            self.get_battery()
            self.get_pitch()
            self.get_barometer()
            self.get_distance()
            self.get_altitude()

    def get_temperature(self):
        temperature = "20°C"  # Здесь можно добавить реальное получение температуры
        self.temp_label.setText(f'Temperature: {temperature}')

    def get_pitch(self):
        pitch = self.tello.get_pitch()
        self.pitch_label.setText(f'Pitch: {pitch}')

    def get_barometer(self):
        barometer = self.tello.get_barometer()
        self.barometer_label.setText(f'Barometer: {barometer}')

    def get_distance(self):
        distance = self.tello.get_distance_tof()
        self.distance_label.setText(f'Distance from Start: {distance} m')

    def get_battery(self):
        battery = self.tello.get_battery()
        self.battery_label.setText(f'Battery: {battery}%')

    def get_altitude(self):
        altitude = self.tello.get_height()
        self.altitude_label.setText(f'Altitude: {altitude} cm')

    def takeoff(self):
        self.tello.takeoff()
        self.temp_label.setText('Drone Taking Off')

    def land(self):
        self.tello.land()
        self.temp_label.setText('Drone Landing')

    def emergency_stop(self):
        self.tello.land()
        self.temp_label.setText('Emergency Stop Activated')

    def move_forward(self):
        self.tello.move_forward(30)
        self.temp_label.setText('Moved Forward')

    def move_back(self):
        self.tello.move_back(30)
        self.temp_label.setText('Moved Back')

    def move_left(self):
        self.tello.move_left(30)
        self.temp_label.setText('Moved Left')

    def move_right(self):
        self.tello.move_right(30)
        self.temp_label.setText('Moved Right')

    def move_up(self):
        self.tello.move_up(30)
        self.temp_label.setText('Moved Up')

    def move_down(self):
        self.tello.move_down(30)
        self.temp_label.setText('Moved Down')

    def closeEvent(self, event):
        self.tello.end()
        event.accept()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #cfcfcf;
            }
            QWidget {
                background-color: #494949;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #cfcfcf;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
            }
        """)

    def set_purple_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #351c75;
            }
            QWidget {
                background-color: #8e7cc3;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #b4a7d6;
                color: #351c75;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7768a4;
            }
        """)

    def set_light_theme(self):
        self.setStyleSheet("""
            QLabel {
                color: #2b2b2b;
            }
            QWidget {
                background-color: #ececec;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #e2e2e2;
                color: #2b2b2b;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-family: 'system', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
        """)

    def switch_theme(self):
        if self.current_theme == 'light':
            self.set_dark_theme()
            self.current_theme = 'dark'
            self.theme_button.setText('Purple Theme')
        elif self.current_theme == 'dark':
            self.set_purple_theme()
            self.current_theme = 'purple'
            self.theme_button.setText('Light Theme')
        else:
            self.set_light_theme()
            self.current_theme = 'light'
            self.theme_button.setText('Dark Theme')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TelloApp()
    ex.show()
    sys.exit(app.exec_())
