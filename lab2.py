import tkinter as tk
import json
import os

class Model:
    def __init__(self):
        self._a = 0
        self._b = 0
        self._c = 0

        self._subscribers = []
        self._is_updating = False

        self.load()
        self._notify()  # одно уведомление при старте

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def _notify(self):
        for callback in self._subscribers:
            callback(self._a, self._b, self._c)

    @property
    def a(self): return self._a

    @property
    def b(self): return self._b

    @property
    def c(self): return self._c

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

        old = (self._a, self._b, self._c)

        new_a = self._a if a is None else self._clamp(a)
        new_b = self._b if b is None else self._clamp(b)
        new_c = self._c if c is None else self._clamp(c)

        if a is not None and new_b < new_a:
            new_b = new_a

        if c is not None and new_b > new_c:
            new_b = new_c

        if b is not None:
            if new_b < new_a:
                new_b = new_a
            if new_b > new_c:
                new_b = new_c

        if new_a > new_c:
            if a is not None:
                new_c = new_a
            elif c is not None:
                new_a = new_c

        if new_b < new_a:
            new_b = new_a
        if new_b > new_c:
            new_b = new_c

        self._a, self._b, self._c = new_a, new_b, new_c

        if (self._a, self._b, self._c) != old:
            self._notify()

        self._is_updating = False

    def _clamp(self, value):
        try:
            value = int(value)
        except:
            value = 0
        return max(0, min(100, value))

    # ---------- Сохранение ----------
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


class App:
    def __init__(self, root, model):
        self.root = root
        self.model = model
        self.updating = False
        self.update_count = 0

        self.root.title("MVC Lab")

        self.create_widgets()

        self.model.subscribe(self.update_view)

    def create_widgets(self):
        tk.Label(self.root, text="A <= B <= C", font=("Arial", 24)) \
            .grid(row=0, column=0, columnspan=3, pady=10)

        self.entries = {}
        self.spins = {}
        self.scales = {}

        for i, name in enumerate(["A", "B", "C"]):
            tk.Label(self.root, text=name, font=("Arial", 16)) \
                .grid(row=1, column=i)

            entry = tk.Entry(self.root, justify="center")
            entry.grid(row=2, column=i, padx=10, pady=5)
            entry.bind("<FocusOut>", lambda e, n=name: self.on_entry(n))
            self.entries[name] = entry

            spin = tk.Spinbox(self.root, from_=0, to=100,
                              justify="center",
                              command=lambda n=name: self.on_spin(n))
            spin.grid(row=3, column=i, padx=10, pady=5)
            self.spins[name] = spin

            scale = tk.Scale(self.root, from_=0, to=100,
                             orient=tk.HORIZONTAL,
                             command=lambda val, n=name: self.on_scale(n, val))
            scale.grid(row=4, column=i, padx=10, pady=5)
            self.scales[name] = scale

    def on_entry(self, name):
        if self.updating:
            return

        value = self.entries[name].get()
        self.set_model(name, value)

    def on_spin(self, name):
        if self.updating:
            return

        value = self.spins[name].get()
        self.set_model(name, value)

    def on_scale(self, name, value):
        if self.updating:
            return

        self.set_model(name, value)

    def set_model(self, name, value):
        if name == "A":
            self.model.set_a(value)
        elif name == "B":
            self.model.set_b(value)
        elif name == "C":
            self.model.set_c(value)

    def update_view(self, a, b, c):
        self.update_count += 1
        print("Обновление:", self.update_count)

        self.updating = True

        values = {"A": a, "B": b, "C": c}

        for name in ["A", "B", "C"]:
            val = values[name]

            self.entries[name].delete(0, tk.END)
            self.entries[name].insert(0, str(val))

            self.spins[name].delete(0, tk.END)
            self.spins[name].insert(0, str(val))

            self.scales[name].set(val)

        self.updating = False


if __name__ == "__main__":
    root = tk.Tk()

    model = Model()
    app = App(root, model)

    def on_close():
        model.save()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()