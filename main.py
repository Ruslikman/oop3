import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor


class CCircle:
    RADIUS = 20  # постоянный радиус

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.selected = False

    def draw(self, painter: QPainter):
        if self.selected:
            painter.setBrush(QColor(255, 0, 0))  # красный если выделен
        else:
            painter.setBrush(QColor(0, 0, 255))  # синий обычный

        painter.drawEllipse(
            self.x - self.RADIUS,
            self.y - self.RADIUS,
            self.RADIUS * 2,
            self.RADIUS * 2
        )

    def contains(self, px, py):
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy <= self.RADIUS * self.RADIUS

    def set_selected(self, value: bool):
        self.selected = value

    def is_selected(self):
        return self.selected

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.circle = CCircle(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.circle.draw(painter)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Круги на форме")
        self.setGeometry(100, 100, 600, 400)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())