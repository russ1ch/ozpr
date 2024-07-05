import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
                             QComboBox, QMessageBox, QLineEdit, QHBoxLayout, QSlider)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageChannelViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.original_img = None
        self.current_img = None
        self.brightness_value = 0

    def initUI(self):
        self.setWindowTitle('ОзПР')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.size_layout = QHBoxLayout()
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText("Ширина")
        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Высота")
        self.resize_button = QPushButton('Изменить размер', self)
        self.resize_button.clicked.connect(self.resize_image)
        self.size_layout.addWidget(self.width_input)
        self.size_layout.addWidget(self.height_input)
        self.size_layout.addWidget(self.resize_button)
        self.layout.addLayout(self.size_layout)

        self.brightness_layout = QHBoxLayout()
        self.brightness_label = QLabel("Яркость:", self)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.brightness_slider.setMinimum(-255)
        self.brightness_slider.setMaximum(255)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.change_brightness)
        self.brightness_layout.addWidget(self.brightness_label)
        self.brightness_layout.addWidget(self.brightness_slider)
        self.layout.addLayout(self.brightness_layout)

        self.circle_layout = QHBoxLayout()
        self.x_input = QLineEdit(self)
        self.x_input.setPlaceholderText("X")
        self.y_input = QLineEdit(self)
        self.y_input.setPlaceholderText("Y")
        self.radius_input = QLineEdit(self)
        self.radius_input.setPlaceholderText("Радиус")
        self.draw_circle_button = QPushButton('Нарисовать круг', self)
        self.draw_circle_button.clicked.connect(self.draw_circle)
        self.circle_layout.addWidget(self.x_input)
        self.circle_layout.addWidget(self.y_input)
        self.circle_layout.addWidget(self.radius_input)
        self.circle_layout.addWidget(self.draw_circle_button)
        self.layout.addLayout(self.circle_layout)

        self.button_load = QPushButton('Загрузить изображение', self)
        self.button_load.clicked.connect(self.load_image)
        self.layout.addWidget(self.button_load)

        self.button_capture = QPushButton('Сделать снимок с веб-камеры', self)
        self.button_capture.clicked.connect(self.capture_image)
        self.layout.addWidget(self.button_capture)

        self.channel_selector = QComboBox(self)
        self.channel_selector.addItems(['Красный', 'Зеленый', 'Синий'])
        self.channel_selector.currentTextChanged.connect(self.show_channel)
        self.layout.addWidget(self.channel_selector)

        self.label_image = QLabel(self)
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_image)

    def load_image(self):
        """Загружает изображение с диска и отображает его в окне."""
        file_path, _ = QFileDialog.getOpenFileName(self, 'Открыть изображение',
                                                   '', 'Image Files (*.png *.jpg)')
        if not file_path:
            QMessageBox.warning(self, 'Ошибка', 'Файл не выбран')
            return

        try:
            self.original_img = cv2.imread(file_path)
            if self.original_img is None:
                raise ValueError('Ошибка при загрузке изображения.')
            self.current_img = self.original_img.copy()
            self.show_image(self.current_img)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка загрузки изображения', str(e))

    def show_image(self, image):
        """Отображает изображение в окне приложения."""
        b, g, r = cv2.split(image)
        image = cv2.merge((r, g, b))  # Преобразование BGR в RGB
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.label_image.setPixmap(pixmap)
        self.label_image.setScaledContents(False)
        self.resize(w, h + 200)

    def capture_image(self):
        """Подключается к веб-камере, делает снимок и отображает его в окне."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к веб-камере.')
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            QMessageBox.critical(self, 'Ошибка', 'Ошибка при захвате изображения с веб-камеры.')
            return

        self.original_img = frame
        self.current_img = self.original_img.copy()
        self.show_image(self.current_img)

    def show_image(self, image):
        """Отображает изображение в окне приложения."""
        b, g, r = cv2.split(image)
        image = cv2.merge((r, g, b))  # Преобразование BGR в RGB
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.label_image.setPixmap(pixmap)
        self.label_image.setScaledContents(False)
        self.resize(w, h + 200)

    def show_channel(self, channel):
        """Отображает выбранный цветовой канал изображения."""
        if self.original_img is None:
            QMessageBox.warning(self, 'Ошибка', 'Изображение не загружено.')
            return

        channels = {'Красный': 2, 'Зеленый': 1, 'Синий': 0}
        channel_index = channels.get(channel)

        if channel_index is None:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный выбор канала.')
            return

        channel_img = np.zeros_like(self.original_img)
        channel_img[:, :, channel_index] = self.original_img[:, :, channel_index]
        self.current_img = channel_img
        self.apply_brightness()

    def resize_image(self, t):
        """Изменяет размер изображения до указанных пользователем размеров."""

        if self.original_img is None:
            QMessageBox.warning(self, 'Ошибка', 'Изображение не загружено.')
            return

        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            if width <= 0 or height <= 0:
                raise ValueError("Размеры должны быть положительными числами.")
            resized_img = cv2.resize(self.original_img, (width, height))
            self.original_img = resized_img
            self.current_img = self.original_img.copy()
            self.apply_brightness()
        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', f'Некорректный ввод: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при изменении размера изображения: {e}')

    def change_brightness(self):
        """Изменяет яркость изображения согласно положению ползунка."""
        if self.original_img is None:
            QMessageBox.warning(self, 'Ошибка', 'Изображение не загружено.')
            return

        self.brightness_value = self.brightness_slider.value()
        self.apply_brightness()

    def adjust_brightness_contrast(self, img, brightness=0, contrast=0):
        """Регулирует яркость изображения."""
        img = img.astype(np.float32)
        img = img + brightness
        img = np.clip(img, 0, 255)
        img = img.astype(np.uint8)
        return img

    def draw_circle(self):
        """Рисует круг на изображении по заданным координатам и радиусу."""
        if self.current_img is None:
            QMessageBox.warning(self, 'Ошибка', 'Изображение не загружено.')
            return

        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            radius = int(self.radius_input.text())
            self.current_img = self.add_circle(self.current_img, x, y, radius)
            self.original_img = self.current_img.copy()  # Обновляем оригинальное изображение
            self.apply_brightness()
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Введите корректные координаты и радиус.')

    def add_circle(self, img, x, y, radius):
        """Добавляет закрашенный круг на изображение."""
        img = cv2.circle(img, (x, y), radius, (0, 0, 255), -1)  # Толщина -1 для закрашенного круга
        return img

    def apply_brightness(self):
        """Применяет яркость к текущему изображению."""
        adjusted_img = self.adjust_brightness_contrast(self.current_img.copy(), self.brightness_value, 0)
        self.show_image(adjusted_img)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageChannelViewer()
    viewer.show()
    sys.exit(app.exec())
