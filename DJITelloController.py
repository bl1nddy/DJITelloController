import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from djitellopy import Tello
import mediapipe as mp

MOVE_DISTANCE = 30  
class TelloApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tello = Tello()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Настройка для распознавания лиц
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Настройка для распознавания жестов
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

    def initUI(self):
        self.setWindowTitle('Tello программа для управления')
        self.setGeometry(100, 100, 800, 600)

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

        self.movement_layout = QGridLayout()

        self.create_movement_buttons()

        self.layout.addLayout(self.movement_layout)

        control_layout = QHBoxLayout()

        self.create_control_buttons(control_layout)

        self.layout.addLayout(control_layout)

        self.setLayout(self.layout)

    def create_movement_buttons(self):
        self.up_button = QPushButton('Лететь вверх')
        self.up_button.setFixedSize(150, 50)
        self.up_button.clicked.connect(self.move_up)
        self.movement_layout.addWidget(self.up_button, 0, 1)

        self.left_button = QPushButton('Двигаться влево')
        self.left_button.setFixedSize(150, 50)
        self.left_button.clicked.connect(self.move_left)
        self.movement_layout.addWidget(self.left_button, 1, 0)

        self.forward_button = QPushButton('Двигаться вперед')
        self.forward_button.setFixedSize(150, 50)
        self.forward_button.clicked.connect(self.move_forward)
        self.movement_layout.addWidget(self.forward_button, 1, 1)

        self.right_button = QPushButton('Двигаться вправо')
        self.right_button.setFixedSize(150, 50)
        self.right_button.clicked.connect(self.move_right)
        self.movement_layout.addWidget(self.right_button, 1, 2)

        self.back_button = QPushButton('Двигаться назад')
        self.back_button.setFixedSize(150, 50)
        self.back_button.clicked.connect(self.move_back)
        self.movement_layout.addWidget(self.back_button, 2, 1)

        self.down_button = QPushButton('Лететь вниз')
        self.down_button.setFixedSize(150, 50)
        self.down_button.clicked.connect(self.move_down)
        self.movement_layout.addWidget(self.down_button, 0, 2)

        # Добавляем кнопки для поворота
        self.rotate_left_button = QPushButton('Поворот против часовой')
        self.rotate_left_button.setFixedSize(150, 50)
        self.rotate_left_button.clicked.connect(self.rotate_left)
        self.movement_layout.addWidget(self.rotate_left_button, 2, 0)

        self.rotate_right_button = QPushButton('Поворот по часовой')
        self.rotate_right_button.setFixedSize(150, 50)
        self.rotate_right_button.clicked.connect(self.rotate_right)
        self.movement_layout.addWidget(self.rotate_right_button, 2, 2)

    def create_control_buttons(self, control_layout):
        self.connect_button = QPushButton('Подключиться к Tello')
        self.connect_button.setFixedSize(150, 50)
        self.connect_button.clicked.connect(self.connect_to_tello)
        control_layout.addWidget(self.connect_button)

        self.takeoff_button = QPushButton('Взлететь')
        self.takeoff_button.setFixedSize(150, 50)
        self.takeoff_button.clicked.connect(self.takeoff)
        control_layout.addWidget(self.takeoff_button)

        self.land_button = QPushButton('Преземлиться')
        self.land_button.setFixedSize(150, 50)
        self.land_button.clicked.connect(self.land)
        control_layout.addWidget(self.land_button)

        self.emergency_stop_button = QPushButton('Экстренная посадка')
        self.emergency_stop_button.setFixedSize(150, 50)
        self.emergency_stop_button.clicked.connect(self.emergency_stop)
        control_layout.addWidget(self.emergency_stop_button)

    def connect_to_tello(self):
        try:
            self.tello.connect()
            self.tello.streamon()
            self.temp_label.setText('Подключено к Tello')
            self.timer.start(20)
        except Exception as e:
            self.temp_label.setText(f'Ошибка: {str(e)}')

    def update_frame(self):
        frame = self.tello.get_frame_read().frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Распознавание лиц и жестов
        frame = self.recognize_face_and_gesture(frame)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))
        self.update_sensor_data()

    def recognize_face_and_gesture(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Применение детектора лиц
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)
        
        # Рисуем рамки вокруг найденных лиц
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Обработка жестов
        result = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return frame

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
        self.temp_label.setText('Дрон преземляется...')
        self.get_battery()

    def emergency_stop(self):
        self.tello.land()
        self.temp_label.setText('Экстренная посадка дрона...')

    def move_forward(self):
        self.tello.move_forward(MOVE_DISTANCE)
        self.temp_label.setText('Пролетел вперед')
        self.get_battery()

    def move_back(self):
        self.tello.move_back(MOVE_DISTANCE)
        self.temp_label.setText('Пролетел назад')Z
        self.get_battery()

    def move_left(self):
        self.tello.move_left(MOVE_DISTANCE)
        self.temp_label.setText('Пролетел влево')
        self.get_battery()

    def move_right(self):
        self.tello.move_right(MOVE_DISTANCE)
        self.temp_label.setText('Пролетел вправо')
        self.get_battery()

    def move_up(self):
        self.tello.move_up(MOVE_DISTANCE)
        self.temp_label.setText('Поднялся вверх')
        self.get_battery()

    def move_down(self):
        self.tello.move_down(MOVE_DISTANCE)
        self.temp_label.setText('Опустился вниз')
        self.get_battery()
    
    def rotate_left(self):
        self.tello.rotate_counter_clockwise(90)  # Поворачиваем на 90 градусов против часовой
        self.temp_label.setText('Повернулся против часовой стрелки')

    def rotate_right(self):
        self.tello.rotate_clockwise(90)  # Поворачиваем на 90 градусов по часовой
        self.temp_label.setText('Повернулся по часовой стрелке')

    def closeEvent(self, event):
        self.tello.end()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TelloApp()
    ex.show()
    sys.exit(app.exec_())
