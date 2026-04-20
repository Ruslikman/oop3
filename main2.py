import sys
import json
import os
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIntValidator, QFont


class Model(QObject):
    data_changed = pyqtSignal()

    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self):
        super().__init__()
        self._a = self.MIN_VALUE
        self._b = (self.MIN_VALUE + self.MAX_VALUE) // 2
        self._c = self.MAX_VALUE
        self._update_count = 0
        self._file_path = "model_data.json"

        self._load_without_notify()
        self._notify_change()

    def get_min_value(self) -> int:
        return self.MIN_VALUE

    def get_max_value(self) -> int:
        return self.MAX_VALUE

    def get_update_count(self) -> int:
        return self._update_count

    def _notify_change(self):
        self._update_count += 1
        self.data_changed.emit()

    def get_a(self) -> int:
        return self._a

    def get_b(self) -> int:
        return self._b

    def get_c(self) -> int:
        return self._c

    def set_a(self, value: int):
        old_a, old_b, old_c = self._a, self._b, self._c
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        new_a = value
        new_b = self._b
        new_c = self._c

        if new_a > new_c:
            new_a = new_c

        if new_a > new_b:
            new_b = new_a

        self._a = new_a
        self._b = new_b
        self._c = new_c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def set_b(self, value: int):
        old_b = self._b
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        if self._a <= value <= self._c:
            self._b = value
            if old_b != self._b:
                self._notify_change()

    def set_c(self, value: int):
        old_a, old_b, old_c = self._a, self._b, self._c
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        new_c = value
        new_a = self._a
        new_b = self._b

        if new_c < new_a:
            new_c = new_a

        if new_c < new_b:
            new_b = new_c

        self._a = new_a
        self._b = new_b
        self._c = new_c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def set_all(self, a: int, b: int, c: int):
        old_a, old_b, old_c = self._a, self._b, self._c

        a = max(self.MIN_VALUE, min(self.MAX_VALUE, a))
        b = max(self.MIN_VALUE, min(self.MAX_VALUE, b))
        c = max(self.MIN_VALUE, min(self.MAX_VALUE, c))

        if a > c:
            a, c = c, a
        if b < a:
            b = a
        if b > c:
            b = c

        self._a = a
        self._b = b
        self._c = c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def save(self):
        try:
            data = {'a': self._a, 'b': self._b, 'c': self._c}
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def _load_without_notify(self):
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    a = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('a', self.MIN_VALUE)))
                    b = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('b', (self.MIN_VALUE + self.MAX_VALUE) // 2)))
                    c = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('c', self.MAX_VALUE)))

                    if a > c:
                        a, c = c, a
                    if b < a:
                        b = a
                    if b > c:
                        b = c

                    self._a = a
                    self._b = b
                    self._c = c
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            self._a = self.MIN_VALUE
            self._b = (self.MIN_VALUE + self.MAX_VALUE) // 2
            self._c = self.MAX_VALUE


class NumberWidget(QWidget):
    value_changed = pyqtSignal(int)

    def __init__(self, label: str, min_val: int, max_val: int, initial_value: int = 0, role: str = "B"):
        super().__init__()
        self.current_value = initial_value
        self.min_val = min_val
        self.max_val = max_val
        self.role = role
        self.a_value = 0
        self.c_value = max_val

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        title_layout = QHBoxLayout()
        self.title_label = QLabel(label)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #FFB347;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        input_row = QHBoxLayout()
        self.text_edit = QLineEdit()
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_edit.setValidator(QIntValidator(min_val, max_val))
        self.text_edit.setText(str(initial_value))
        self.text_edit.editingFinished.connect(self.on_editing_finished)
        self.text_edit.textChanged.connect(self.on_text_changed)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(min_val, max_val)
        self.spin_box.setValue(initial_value)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.valueChanged.connect(self.on_spin_changed)

        input_row.addWidget(self.text_edit)
        input_row.addWidget(self.spin_box)
        input_row.setSpacing(10)
        main_layout.addLayout(input_row)

        # Слайдер
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(initial_value)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.on_slider_changed)
        main_layout.addWidget(self.slider)

        self.setLayout(main_layout)
        self._updating = False

        self.setStyleSheet("""
            NumberWidget {
                background-color: #2D2A2E;
                border-radius: 16px;
                border: 1px solid #FFB347;
            }
            QLineEdit {
                background-color: #1E1C1F;
                border: 1px solid #FFB347;
                border-radius: 12px;
                padding: 8px;
                color: #FFE0B5;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #FF8C00;
            }
            QSpinBox {
                background-color: #1E1C1F;
                border: 1px solid #FFB347;
                border-radius: 12px;
                padding: 6px;
                color: #FFE0B5;
                font-size: 13px;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border-radius: 6px;
                background-color: #3A3538;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #FFB347;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #3A3538;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFB347;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #FF8C00;
                transform: scale(1.2);
            }
            QSlider::sub-page:horizontal {
                background: #FFB347;
                border-radius: 3px;
            }
        """)

    def set_bounds(self, a: int, c: int):
        self.a_value = a
        self.c_value = c

    def is_value_allowed(self, value: int) -> bool:
        if self.role == 'A':
            return value <= self.c_value
        elif self.role == 'C':
            return value >= self.a_value
        elif self.role == 'B':
            return self.a_value <= value <= self.c_value
        return True

    def update_value(self, value: int):
        if self._updating:
            return

        self._updating = True
        self.current_value = value
        self.text_edit.setText(str(value))
        self.spin_box.setValue(value)
        self.slider.setValue(value)
        self._updating = False

    def on_text_changed(self, text: str):
        if self._updating:
            return
        try:
            if text and text != "-":
                value = int(text)
                if self.min_val <= value <= self.max_val and self.is_value_allowed(value):
                    self.value_changed.emit(value)
        except ValueError:
            pass

    def on_editing_finished(self):
        if self._updating:
            return

        try:
            text = self.text_edit.text()
            if not text or text == "-":
                self.update_value(self.current_value)
                return

            value = int(text)
            if not (self.min_val <= value <= self.max_val and self.is_value_allowed(value)):
                self.update_value(self.current_value)
                return
        except ValueError:
            self.update_value(self.current_value)

    def on_spin_changed(self, value: int):
        if not self._updating:
            if self.is_value_allowed(value):
                self.value_changed.emit(value)
            else:
                self.update_value(self.current_value)

    def on_slider_changed(self, value: int):
        if not self._updating:
            if self.is_value_allowed(value):
                self.value_changed.emit(value)
            else:
                self.update_value(self.current_value)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.current_value != self.spin_box.value():
            self.update_value(self.current_value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №3 — Управление параметрами")
        self.setMinimumSize(900, 350)
        self.resize(1000, 400)

        self.model = Model()
        self.model.data_changed.connect(self.on_model_changed)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel(" A <= B <= C")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFB347; padding: 10px;")
        main_layout.addWidget(header)

        numbers_layout = QHBoxLayout()
        numbers_layout.setSpacing(20)

        min_val = self.model.get_min_value()
        max_val = self.model.get_max_value()

        self.widget_a = NumberWidget("Число A", min_val, max_val, self.model.get_a(), role='A')
        self.widget_b = NumberWidget("Число B", min_val, max_val, self.model.get_b(), role='B')
        self.widget_c = NumberWidget("Число C", min_val, max_val, self.model.get_c(), role='C')

        self.widget_a.value_changed.connect(self.on_a_changed)
        self.widget_b.value_changed.connect(self.on_b_changed)
        self.widget_c.value_changed.connect(self.on_c_changed)

        numbers_layout.addWidget(self.widget_a)
        numbers_layout.addWidget(self.widget_b)
        numbers_layout.addWidget(self.widget_c)

        main_layout.addLayout(numbers_layout)

        self.update_label = QLabel()
        self.update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_label.setStyleSheet("color: #C0C0C0; font-size: 12px; padding: 8px; background-color: #1E1C1F; border-radius: 12px;")
        main_layout.addWidget(self.update_label)

        self.on_model_changed()
        self.apply_window_style()

    def apply_window_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1C1F;
            }
            QWidget {
                background-color: #1E1C1F;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)

    def on_a_changed(self, value: int):
        self.model.set_a(value)

    def on_b_changed(self, value: int):
        self.model.set_b(value)

    def on_c_changed(self, value: int):
        self.model.set_c(value)

    def on_model_changed(self):
        a = self.model.get_a()
        b = self.model.get_b()
        c = self.model.get_c()

        self.widget_a.set_bounds(a, c)
        self.widget_b.set_bounds(a, c)
        self.widget_c.set_bounds(a, c)

        self.widget_a.update_value(a)
        self.widget_b.update_value(b)
        self.widget_c.update_value(c)


    def closeEvent(self, event):
        self.model.save()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()