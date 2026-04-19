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
class CircleStorage:
    def __init__(self):
        self._data = []      # приватное хранилище
        self._index = 0      # для итерации

    def add(self, circle):
        self._data.append(circle)

    # --- итерация ---
    def first(self):
        self._index = 0

    def next(self):
        self._index += 1

    def eol(self):
        return self._index >= len(self._data)

    def getObject(self):
        if not self.eol():
            return self._data[self._index]
        return None

    # --- дополнительные методы ---
    def remove_selected(self):
        self._data = [c for c in self._data if not c.is_selected()]

    def clear_selection(self):
        for c in self._data:
            c.set_selected(False)

    def get_all(self):
        return self._data

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.storage = CircleStorage()

        # временно добавим пару кругов для проверки
        self.storage.add(CCircle(100, 100))
        self.storage.add(CCircle(200, 150))

    def paintEvent(self, event):
        painter = QPainter(self)

        self.storage.first()
        while not self.storage.eol():
            circle = self.storage.getObject()
            circle.draw(painter)
            self.storage.next()


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