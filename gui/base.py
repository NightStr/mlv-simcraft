import json
import os
import tkinter as tk
from contextlib import suppress
from tkinter import ttk, filedialog, messagebox


class BaseTkView:
    TITLE: str = "Simulation GUI"
    DEFAULTS: dict[str, str] = {}

    def __init__(self, root):
        self.entries: dict[str, tk.Entry] = {}
        self.load_defaults()
        self.root = root
        self.root.title(self.TITLE)
        self.root.resizable(False, False)

        # Main frame setup
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Input fields and result display
        self.setup_input_fields()

        self.result_text = tk.Text(self.main_frame, width=40, height=10)
        self.result_text.grid(column=2, row=0, rowspan=13, padx=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.progress = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.progress.grid(column=0, row=13, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.start_button = ttk.Button(self.main_frame, text="Start Simulation", command=self.start_simulation_thread)
        self.start_button.grid(column=0, row=14, columnspan=3, sticky=(tk.W, tk.E))
        self.running = False
        self.thread = None
        root.protocol("WM_DELETE_WINDOW", self.destroy_root(root))
        self.create_menu(root)

    def save_data(self):
        self.create_saves_dir()
        file_name = filedialog.asksaveasfilename(
            initialdir="./saves/",
            defaultextension=".json", filetypes=[("saves", "*.json"), ("All files", "*.*")]
        )
        if file_name:
            try:
                self.save_defaults(file_name)
                messagebox.showinfo("Информация", "Файл успешно сохранен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_data(self):
        self.create_saves_dir()
        file_name = filedialog.askopenfilename(
            initialdir="./saves/",
            filetypes=[("Save files", "*.json"), ("All files", "*.*")]
        )
        if file_name:
            try:
                self.load_defaults(file_name)
                messagebox.showinfo("Информация", "Файл успешно загружен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def create_menu(self, window):
        menu_bar = tk.Menu(window)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Сохранить", command=self.save_data)
        file_menu.add_command(label="Загрузить", command=self.load_data)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        window.config(menu=menu_bar)

    def update_defaults(self):
        for key, value in self.DEFAULTS.items():
            self.DEFAULTS[key] = self.entries[key].get()

    def update_entries(self):
        for key, value in self.DEFAULTS.items():
            if entry := self.entries.get(key):
                entry.delete(0, tk.END)
                entry.insert(0, self.DEFAULTS[key])

    def create_saves_dir(self):
        os.makedirs('saves', exist_ok=True)

    def save_defaults(self, file_name: str | None = None):
        self.create_saves_dir()
        self.update_defaults()
        file_name = file_name or f"saves/{self.__class__.__name__}_defaults.json"
        with open(file_name, "w") as defaults_file:
            json.dump(self.DEFAULTS, defaults_file)

    def load_defaults(self, file_name: str | None = None):
        file_name = file_name or f"saves/{self.__class__.__name__}_defaults.json"
        with suppress(FileNotFoundError):
            with open(file_name, "r") as defaults_file:
                loaded_defaults = json.load(defaults_file)
            for k, v in loaded_defaults.items():
                if k in self.DEFAULTS:
                    self.DEFAULTS[k] = v
        self.update_entries()

    def destroy_root(self, root):
        def destroy_fn():
            self.save_defaults()
            root.destroy()

        return destroy_fn

    def setup_input_fields(self):
        for idx, (label, value) in enumerate(self.DEFAULTS.items()):
            label = ttk.Label(self.main_frame, text=f"{label}:")
            label.grid(column=0, row=idx, sticky=tk.W, pady=2)

            entry = ttk.Entry(self.main_frame, width=7)
            entry.grid(column=1, row=idx, sticky=(tk.W, tk.E), pady=2)
            entry.insert(0, value)
            self.entries[label.cget("text")[:-1]] = entry
