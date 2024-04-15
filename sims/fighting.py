from typing import NamedTuple

import numpy as np
from tqdm import tqdm

from core import sec_to_time

RESPAWN_TIME = 3


class FightingSimResult(NamedTuple):
    time: int
    enemy_killed: int


class FightingSimConfig(NamedTuple):
    player_health: int
    player_health_regen: int
    player_regen_interval: int
    player_damage_min: int
    player_damage_max: int
    player_hit_chance: float
    player_attack_interval: float

    enemy_health: int
    enemy_damage_min: int
    enemy_damage_max: int
    enemy_hit_chance: float
    enemy_attack_interval: float


# Simulation function
def simulate_battle(config: FightingSimConfig) -> FightingSimResult:
    player_current_health = config.player_health
    time = 0
    enemy_killed = 0
    regen_timer = 0
    enemy_current_health = config.enemy_health

    while player_current_health > 0 and time < 5 * 60 * 60:
        # Player attacks
        attack_roll = round(np.random.rand(), 2)
        if attack_roll <= config.player_hit_chance:
            enemy_current_health -= np.random.randint(config.player_damage_min, config.player_damage_max + 1)
            if enemy_current_health <= 0:
                enemy_current_health = config.enemy_health
                time += RESPAWN_TIME  # Waiting for next enemy to respawn
                enemy_killed += 1
                continue

        # Enemy attacks
        enemy_attack_roll = round(np.random.rand(), 2)
        if enemy_attack_roll <= config.enemy_hit_chance:
            player_current_health -= np.random.randint(config.enemy_damage_min, config.enemy_damage_max + 1)

        # Health regeneration for the player
        regen_timer = regen_timer + config.player_attack_interval
        while regen_timer >= config.player_regen_interval:
            player_current_health += config.player_health_regen
            regen_timer -= config.player_regen_interval

        # Update time
        time += config.player_attack_interval

        # Health cap
        player_current_health = min(player_current_health, config.player_health)

    return FightingSimResult(time=time, enemy_killed=enemy_killed)


def format_fighting_results(results: list[FightingSimResult]) -> str:
    simulations_time_results = [r.time for r in results]
    enemy_killed = [r.enemy_killed for r in results]

    mean_time = sec_to_time(int(np.mean(simulations_time_results)))
    median_time = sec_to_time(int(np.median(simulations_time_results)))
    min_time = sec_to_time(int(np.min(simulations_time_results)))
    max_time = sec_to_time(int(np.max(simulations_time_results)))

    mean_killed = int(np.mean(enemy_killed))
    median_killed = int(np.median(enemy_killed))
    min_killed = int(np.min(enemy_killed))
    max_killed = int(np.max(enemy_killed))

    return (
        f"Mean time: {mean_time}\n" +
        f"Median time: {median_time}\n" +
        f"Min time: {min_time}\n" +
        f"Max time: {max_time}\n" +
        "-"*20 + "\n" +
        f"Mean killed: {mean_killed}\n" +
        f"Median killed: {median_killed}\n" +
        f"Min killed: {min_killed}\n" +
        f"Max killed: {max_killed}"
    )


if __name__ == "__main__":
    # Running the simulation multiple times
    config = FightingSimConfig(
        player_health=720,
        player_health_regen=8,
        player_regen_interval=8,
        player_damage_min=1,
        player_damage_max=111,
        player_hit_chance=0.76,
        player_attack_interval=3.0,
        enemy_health=300,
        enemy_damage_min=0,
        enemy_damage_max=116,
        enemy_hit_chance=0.35,
        enemy_attack_interval=2.4,
    )
    results = []
    for _ in tqdm(range(5_000), desc="Fight simulation"):
        results.append(simulate_battle(config))
    print(format_fighting_results(results))
