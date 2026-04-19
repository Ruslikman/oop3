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
            painter.setBrush(QColor(255, 0, 0))
        else:
            painter.setBrush(QColor(0, 0, 255))

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
        self._index = 0      # для итерацииb

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

    def remove_selected(self):
        self._data = [c for c in self._data if not c.is_selected()]

    def clear_selection(self):
        for c in self._data:
            c.set_selected(False)

    def get_all(self):
        return self._data

    def find_at(self, x, y): #выд. верхнего
        for circle in reversed(self._data):
            if circle.contains(x, y):
                return circle
        return None

    def find_all_at(self, x, y):
        result = []
        for circle in self._data:
            if circle.contains(x, y):
                result.append(circle)
        return result

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.storage = CircleStorage()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()


    def paintEvent(self, event):
        painter = QPainter(self)

        self.storage.first()
        while not self.storage.eol():
            circle = self.storage.getObject()
            circle.draw(painter)
            self.storage.next()

    def mousePressEvent(self, event):
        self.setFocus()

        if event.button() == Qt.MouseButton.LeftButton:
            x = int(event.position().x())
            y = int(event.position().y())

            modifiers = event.modifiers()

            # универсально: Ctrl (Win) или ⌘ (Mac)
            multi_select = (modifiers & Qt.KeyboardModifier.ControlModifier)

            if multi_select:
                circles = self.storage.find_all_at(x, y)

                for c in circles:
                    c.set_selected(not c.is_selected())

            else:
                clicked_circle = self.storage.find_at(x, y)

                self.storage.clear_selection()

                if clicked_circle:
                    clicked_circle.set_selected(True)
                else:
                    self.storage.add(CCircle(x, y))

            self.update()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.storage.remove_selected()
            self.update()

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