import decimal
import os
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Thread

from gui.base import BaseTkView
from sims.fighting import simulate_battle, FightingSimConfig, FightingSimResult, format_fighting_results


class FightingSimulationApp(BaseTkView):
    TITLE = "Fighting Simulation GUI"
    DEFAULTS = {
        "Player Health": "720",
        "Player Health Regen": "8",
        "Player Regen Interval": "8",
        "Player Damage Min": "1",
        "Player Damage Max": "111",
        "Player Hit Chance": "76",
        "Player Attack Interval": "3.0",
        "Enemy Health": "300",
        "Enemy Damage Min": "0",
        "Enemy Damage Max": "116",
        "Enemy Hit Chance": "35",
        "Enemy Attack Interval": "2.4",
        "Iterations": "5000",
    }
    DEFAULTEXTENSION = 'fsave'

    def start_simulation_thread(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.start_simulation)
            self.thread.start()
            self.start_button.config(text="Stop Simulation")
        else:
            self.progress['value'] = 0
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
            player_attack_interval=decimal.Decimal(self.entries["Player Attack Interval"].get()),
            enemy_health=int(self.entries["Enemy Health"].get()),
            enemy_damage_min=int(self.entries["Enemy Damage Min"].get()),
            enemy_damage_max=int(self.entries["Enemy Damage Max"].get()),
            enemy_hit_chance=float(self.entries["Enemy Hit Chance"].get()) / 100,
            enemy_attack_interval=decimal.Decimal(self.entries["Enemy Attack Interval"].get())
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
    app = FightingSimulationApp(root)
    root.mainloop()
