import os
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor, as_completed
from tkinter import ttk
import decimal
from threading import Thread

from sims.thieving import sim, ThievingSimConfig, ThievingSimResult, format_thieve_results


class App:
    TITLE = "Thieve Simulation GUI"
    LABELS = [
        ("Health Regeneration Interval", "8"),
        ("Health Regeneration Amount", "8"),
        ("Max Health", "720"),
        ("Steal Interval", "2.6"),
        ("Steal Success Chance", "57"),
        ("Min Damage", "0"),
        ("Max Damage", "157"),
        ("Min Gold", "50"),
        ("Max Gold", "1100"),
        ("Iterations", "5000")
    ]

    def __init__(self, root):
        self.root = root
        self.root.title(self.TITLE)
        self.root.resizable(False, False)

        # Создание основного фрейма
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка расширяемости виджетов и окна
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Создание и размещение полей ввода и результатов
        self.setup_input_fields()

        # Создание и размещение виджета для вывода результатов
        self.result_text = tk.Text(self.main_frame, width=40, height=10)
        self.result_text.grid(column=2, row=0, rowspan=11, padx=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Прогресс бар для отображения прогресса симуляции
        self.progress = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.progress.grid(column=0, row=11, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Кнопка для запуска и остановки симуляции
        self.start_button = ttk.Button(self.main_frame, text="Start Simulation", command=self.start_simulation_thread)
        self.start_button.grid(column=0, row=12, columnspan=3, sticky=(tk.W, tk.E))
        self.running = False
        self.thread = None

    def setup_input_fields(self):

        self.entries = {}
        for idx, (label, value) in enumerate(self.LABELS):
            label = ttk.Label(self.main_frame, text=f"{label}:")
            label.grid(column=0, row=idx, sticky=tk.W, pady=2)

            entry = ttk.Entry(self.main_frame, width=7)
            entry.grid(column=1, row=idx, sticky=(tk.W, tk.E), pady=2)
            entry.insert(0, value)
            self.entries[label.cget("text")[:-1]] = entry

    def start_simulation_thread(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.start_simulation)
            self.thread.start()
            self.start_button.config(text="Stop Simulation")
        else:
            self.progress['value'] = 0
            self.start_button.config(text="Start Simulation")
            self.running = False

    def build_sim_config(self) -> ThievingSimConfig:
        return ThievingSimConfig(
            health_regeneration_interval=int(self.entries["Health Regeneration Interval"].get()),
            health_regeneration_amount=int(self.entries["Health Regeneration Amount"].get()),
            max_health=int(self.entries["Max Health"].get()),
            steal_interval=decimal.Decimal(self.entries["Steal Interval"].get()),
            steal_success_chance=float(self.entries["Steal Success Chance"].get()) / 100,
            min_damage=int(self.entries["Min Damage"].get()),
            max_damage=int(self.entries["Max Damage"].get()),
            min_gold=int(self.entries["Min Gold"].get()),
            max_gold=int(self.entries["Max Gold"].get())
        )

    def start_simulation(self):
        iterations = int(self.entries["Iterations"].get())
        config = self.build_sim_config()

        # Определение количества процессов
        max_workers = os.cpu_count() - 1 if os.cpu_count() > 1 else 1

        results = []
        self.progress['maximum'] = iterations
        self.progress['value'] = 0

        # Запуск процессов для выполнения симуляций
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(sim, config) for _ in range(iterations)]
            for future in as_completed(futures):
                if not self.running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                result = future.result()
                results.append(result)
                self.update_result_display(results)
                self.progress['value'] += 1
                self.root.update_idletasks()  # Обновление интерфейса и прогресс бара

        if self.running:
            self.update_result_display(results)
            self.start_button.config(text="Start Simulation")
            self.running = False

    def update_result_display(self, results: list[ThievingSimResult]):
        # Очистка виджета вывода и вывод результатов
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, format_thieve_results(results))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
