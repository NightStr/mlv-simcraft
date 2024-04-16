import os
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor, as_completed
import decimal
from threading import Thread

from gui.base import BaseTkView
from sims.thieving import sim, ThievingSimConfig, ThievingSimResult, format_thieve_results


class ThievingSimulationApp(BaseTkView):
    TITLE = "Thieving Simulation GUI"
    DEFAULTS = {
        "Health Regeneration Interval": "8",
        "Health Regeneration Amount": "8",
        "Max Health": "720",
        "Steal Interval": "2.6",
        "Steal Success Chance": "57",
        "Min Damage": "0",
        "Max Damage": "157",
        "Min Gold": "50",
        "Max Gold": "1100",
        "Iterations": "5000",
    }
    DEFAULTEXTENSION = 'thsave'

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
    app = ThievingSimulationApp(root)
    root.mainloop()
