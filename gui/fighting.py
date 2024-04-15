import os
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Thread

from core import sec_to_time
from sims.fighting import simulate_battle, FightingSimConfig, FightingSimResult, format_fighting_results


class App:
    TITLE = "Fighting Simulation GUI"
    LABELS = [
        ("Player Health", "720"),
        ("Player Health Regen", "8"),
        ("Player Regen Interval", "8"),
        ("Player Damage Min", "1"),
        ("Player Damage Max", "111"),
        ("Player Hit Chance", "76"),
        ("Player Attack Interval", "3.0"),
        ("Enemy Health", "300"),
        ("Enemy Damage Min", "0"),
        ("Enemy Damage Max", "116"),
        ("Enemy Hit Chance", "35"),
        ("Enemy Attack Interval", "2.4"),
        ("Iterations", "5000")
    ]

    def __init__(self, root):
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
            self.running = False
            self.start_button.config(text="Start Simulation")

    def build_sim_config(self) -> FightingSimConfig:
        return FightingSimConfig(
            player_health=int(self.entries["Player Health"].get()),
            player_health_regen=int(self.entries["Player Health Regen"].get()),
            player_regen_interval=int(self.entries["Player Regen Interval"].get()),
            player_damage_min=int(self.entries["Player Damage Min"].get()),
            player_damage_max=int(self.entries["Player Damage Max"].get()),
            player_hit_chance=float(self.entries["Player Hit Chance"].get()) / 100,
            player_attack_interval=float(self.entries["Player Attack Interval"].get()),
            enemy_health=int(self.entries["Enemy Health"].get()),
            enemy_damage_min=int(self.entries["Enemy Damage Min"].get()),
            enemy_damage_max=int(self.entries["Enemy Damage Max"].get()),
            enemy_hit_chance=float(self.entries["Enemy Hit Chance"].get()) / 100,
            enemy_attack_interval=float(self.entries["Enemy Attack Interval"].get())
        )

    def start_simulation(self):
        iterations = int(self.entries["Iterations"].get())
        config = self.build_sim_config()

        max_workers = os.cpu_count() - 1 if os.cpu_count() > 1 else 1
        results = []
        self.progress['maximum'] = iterations
        self.progress['value'] = 0

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(simulate_battle, config) for _ in range(iterations)]
            for future in as_completed(futures):
                if not self.running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                result = future.result()
                results.append(result)
                self.update_result_display(results)
                self.progress['value'] += 1
                self.root.update_idletasks()

        if self.running:
            self.update_result_display(results)
            self.start_button.config(text="Start Simulation")
            self.running = False

    def update_result_display(self, results: list[FightingSimResult]):
        formatted_results = format_fighting_results(results)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, formatted_results)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
