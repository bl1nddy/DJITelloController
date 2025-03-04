import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from djitellopy import Tello

MOVE_DISTANCE = 30  

class TelloApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tello = Tello()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Инициализация веб-камеры
        self.cap = cv2.VideoCapture(0)

        # Установка начальной темы
        self.dark_theme = False
        self.set_light_theme()

    def initUI(self):
        self.setWindowTitle('Tello управление с помощью жестов')
        self.setGeometry(100, 100, 960, 540)  # Установка разрешения окна

        self.layout = QVBoxLayout()

        self.video_label = QLabel('Живая трансляция')
        self.layout.addWidget(self.video_label)

        info_layout = QVBoxLayout()
        self.temp_label = QLabel('Температура:')
        info_layout.addWidget(self.temp_label)

        self.pitch_label = QLabel('Наклон:')
        info_layout.addWidget(self.pitch_label)

        self.barometer_label = QLabel('Барометр:')
        info_layout.addWidget(self.barometer_label)

        self.distance_label = QLabel('Расстояние со старта:')
        info_layout.addWidget(self.distance_label)

        self.battery_label = QLabel('Батарея:')
        info_layout.addWidget(self.battery_label)

        self.altitude_label = QLabel('Высота:')
        info_layout.addWidget(self.altitude_label)

        self.speed_label = QLabel('Скорость:')
        info_layout.addWidget(self.speed_label)

        self.layout.addLayout(info_layout)

        control_layout = QHBoxLayout()
        self.create_control_buttons(control_layout)
        self.layout.addLayout(control_layout)

        # Кнопка для смены темы
        self.theme_button = QPushButton('Сменить тему')
        self.theme_button.setFixedSize(150, 50)
        self.theme_button.clicked.connect(self.toggle_theme)
        control_layout.addWidget(self.theme_button)

        self.setLayout(self.layout)

    def create_control_buttons(self, control_layout):
        self.connect_button = QPushButton('Подключиться к Tello')
        self.connect_button.setFixedSize(150, 50)
        self.connect_button.clicked.connect(self.connect_to_tello)
        control_layout.addWidget(self.connect_button)

        self.takeoff_button = QPushButton('Взлететь')
        self.takeoff_button.setFixedSize(150, 50)
        self.takeoff_button.clicked.connect(self.takeoff)
        control_layout.addWidget(self.takeoff_button)

        self.land_button = QPushButton('Приземлиться')
        self.land_button.setFixedSize(150, 50)
        self.land_button.clicked.connect(self.land)
        control_layout.addWidget(self.land_button)

        self.emergency_stop_button = QPushButton('Экстренная посадка')
        self.emergency_stop_button.setFixedSize(150, 50)
        self.emergency_stop_button.clicked.connect(self.emergency_stop)
        control_layout.addWidget(self.emergency_stop_button)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        if self.dark_theme:
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #494949;  /* Цвет фона для темной темы */
            }
            QPushButton {
                background-color: #3c3c3c;  /* Цвет фона кнопок для темной темы */
                color: #cfcfcf;              /* Цвет текста кнопок для темной темы */
                border: none;                /* Убираем рамку */
                padding: 10px;               /* Отступы внутри кнопок */
                border-radius: 5px;          /* Закругление углов кнопок */
            }
            QPushButton:hover {
                background-color: #2f2f2f;   /* Цвет кнопки при наведении для темной темы (темнее) */
            }
        """)

    def set_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ececec;  /* Цвет фона для светлой темы */
            }
            QPushButton {
                background-color: #e2e2e2; 
                                           color: #2b2b2b;              /* Цвет текста кнопок для светлой темы */
                border: none;                /* Убираем рамку */
                padding: 10px;               /* Отступы внутри кнопок */
                border-radius: 5px;          /* Закругление углов кнопок */
            }
            QPushButton:hover {
                background-color: #d5d5d5;   /* Цвет кнопки при наведении для светлой темы */
            }
        """)

    def connect_to_tello(self):
        try:
            self.tello.connect()
            self.tello.streamon()
            self.temp_label.setText('Подключено к Tello')
            self.timer.start(20)
        except Exception as e:
            self.temp_label.setText(f'Ошибка: {str(e)}')

    def update_frame(self):
        ret, frame = self.cap.read()  # Чтение с веб-камеры
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Отображение кадра на QLabel
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))
        self.update_sensor_data()

    def update_sensor_data(self):
        self.get_temperature()
        self.get_pitch()
        self.get_barometer()
        self.get_distance()
        self.get_battery()
        self.get_altitude()
        self.get_speed()

    def get_temperature(self):
        temperature = self.tello.get_temperature()
        self.temp_label.setText(f'Температура батареи: {temperature} C')

    def get_pitch(self):
        pitch = self.tello.get_pitch()
        self.pitch_label.setText(f'Наклон Tello: {pitch}')

    def get_barometer(self):
        barometer = self.tello.get_barometer()
        self.barometer_label.setText(f'Барометр: {barometer}')

    def get_distance(self):
        distance = self.tello.get_distance_tof()
        self.distance_label.setText(f'Расстояние от начальной точки: {distance} м')

    def get_battery(self):
        battery = self.tello.get_battery()
        self.battery_label.setText(f'Батарея: {battery}%')

    def get_altitude(self):
        altitude = self.tello.get_height()
        self.altitude_label.setText(f'Высота: {altitude} см')

    def get_speed(self):
        speed = self.tello.get_speed()
        self.speed_label.setText(f'Скорость: {speed} см/с')

    def takeoff(self):
        self.tello.takeoff()
        self.temp_label.setText('Дрон взлетает...')
        self.get_battery()

    def land(self):
        self.tello.land()
        self.temp_label.setText('Дрон приземляется...')
        self.get_battery()

    def emergency_stop(self):
        self.tello.land()
        self.temp_label.setText('Экстренная посадка дрона...')

    def closeEvent(self, event):
        self.tello.end()
        self.cap.release()  # Освобождаем веб-камеру
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TelloApp()
    ex.show()
    sys.exit(app.exec_())
