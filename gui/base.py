import json
import os
import tkinter as tk
from contextlib import suppress
from tkinter import ttk


class BaseTkView:
    TITLE: str = "Simulation GUI"
    DEFAULTS: dict[str, str] = {}

    def __init__(self, root):
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

    def update_defaults(self):
        for key, value in self.DEFAULTS.items():
            self.DEFAULTS[key] = self.entries[key].get()

    def save_defaults(self):
        self.update_defaults()
        os.makedirs('saves', exist_ok=True)
        with open(f"saves/{self.__class__.__name__}_defaults.json", "w") as defaults_file:
            json.dump(self.DEFAULTS, defaults_file)

    def destroy_root(self, root):
        def destroy_fn():
            self.save_defaults()
            root.destroy()

        return destroy_fn

    def load_defaults(self):
        with suppress(FileNotFoundError):
            with open(f"saves/{self.__class__.__name__}_defaults.json", "r") as defaults_file:
                self.DEFAULTS = json.load(defaults_file)

    def setup_input_fields(self):
        self.entries = {}
        for idx, (label, value) in enumerate(self.DEFAULTS.items()):
            label = ttk.Label(self.main_frame, text=f"{label}:")
            label.grid(column=0, row=idx, sticky=tk.W, pady=2)

            entry = ttk.Entry(self.main_frame, width=7)
            entry.grid(column=1, row=idx, sticky=(tk.W, tk.E), pady=2)
            entry.insert(0, value)
            self.entries[label.cget("text")[:-1]] = entry
