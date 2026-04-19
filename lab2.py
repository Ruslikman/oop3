import json
import os

class Model:
    def __init__(self):
        self._a = 0
        self._b = 0
        self._c = 0

        self._subscribers = []
        self._is_updating = False  # защита от множественных уведомлений

        self.load()
        self._notify()  # одно уведомление при старте

    # -------------------- Подписка --------------------
    def subscribe(self, callback):
        self._subscribers.append(callback)

    def _notify(self):
        for callback in self._subscribers:
            callback(self._a, self._b, self._c)

    # -------------------- Геттеры --------------------
    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return self._c

    # -------------------- Установка значений --------------------
    def set_a(self, value):
        self._update(a=value)

    def set_b(self, value):
        self._update(b=value)

    def set_c(self, value):
        self._update(c=value)

    def _update(self, a=None, b=None, c=None):
        if self._is_updating:
            return

        self._is_updating = True

        old_values = (self._a, self._b, self._c)

        # применяем новые значения
        new_a = self._a if a is None else self._clamp(a)
        new_b = self._b if b is None else self._clamp(b)
        new_c = self._c if c is None else self._clamp(c)

        # -------------------- ЛОГИКА --------------------

        # 1. Разрешающее поведение для A и C
        if a is not None:
            if new_b < new_a:
                new_b = new_a

        if c is not None:
            if new_b > new_c:
                new_b = new_c

        # 2. Ограничивающее поведение для B
        if b is not None:
            if new_b < new_a:
                new_b = new_a
            if new_b > new_c:
                new_b = new_c

        # 3. ГЛАВНОЕ — финальная нормализация (гарантия A ≤ B ≤ C)

        # сначала порядок A и C
        if new_a > new_c:
            # разрешающее поведение: сохраняем введённое значение
            if a is not None:
                new_c = new_a
            elif c is not None:
                new_a = new_c

        # потом B между ними
        if new_b < new_a:
            new_b = new_a
        if new_b > new_c:
            new_b = new_c

        # применяем
        self._a, self._b, self._c = new_a, new_b, new_c

        # уведомление только если изменилось
        if (self._a, self._b, self._c) != old_values:
            self._notify()

        self._is_updating = False

    def _clamp(self, value):
        return max(0, min(100, int(value)))

    # -------------------- Сохранение --------------------
    def save(self):
        with open("data.json", "w") as f:
            json.dump({"a": self._a, "b": self._b, "c": self._c}, f)

    def load(self):
        if os.path.exists("data.json"):
            with open("data.json", "r") as f:
                data = json.load(f)
                self._a = data.get("a", 0)
                self._b = data.get("b", 0)
                self._c = data.get("c", 0)

m = Model()

def print_values(a, b, c):
    print(a, b, c)

m.subscribe(print_values)

m.set_a(50)
m.set_b(200)
m.set_c(10)