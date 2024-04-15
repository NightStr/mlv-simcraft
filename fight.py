import numpy as np
from tqdm import tqdm

from core import sec_to_time

# Parameters
player_health = 720
player_health_regen = 8
player_regen_interval = 8
player_damage_min = 1
player_damage_max = 111
player_hit_chance = 0.76
player_attack_interval = 3.0

enemy_health = 300
enemy_damage_min = 0
enemy_damage_max = 116
enemy_hit_chance = 0.35
enemy_attack_interval = 2.4

respawn_time = 3


# Simulation function
def simulate_battle():
    player_current_health = player_health
    time = 0
    enemy_killed = 0
    regen_timer = 0
    enemy_current_health = enemy_health

    while player_current_health > 0 and time < 5 * 60 * 60:
        # Player attacks
        attack_roll = round(np.random.rand(), 2)
        if attack_roll <= player_hit_chance:
            enemy_current_health -= np.random.randint(player_damage_min, player_damage_max + 1)
            if enemy_current_health <= 0:
                enemy_current_health = enemy_health
                time += respawn_time  # Waiting for next enemy to respawn
                enemy_killed += 1
                continue

        # Enemy attacks
        enemy_attack_roll = round(np.random.rand(), 2)
        if enemy_attack_roll <= enemy_hit_chance:
            player_current_health -= np.random.randint(enemy_damage_min, enemy_damage_max + 1)

        # Health regeneration for the player
        regen_timer = regen_timer + player_attack_interval
        while regen_timer >= player_regen_interval:
            player_current_health += player_health_regen
            regen_timer -= player_regen_interval

        # Update time
        time += player_attack_interval

        # Health cap
        player_current_health = min(player_current_health, player_health)

    return time, enemy_killed

# Running the simulation multiple times
num_simulations = 5000
simulations_time_results = []
enemy_killed = []
for _ in tqdm(range(num_simulations)):
    simulation_time, killed = simulate_battle()
    simulations_time_results.append(simulation_time)
    enemy_killed.append(killed)

# Calculating statistics
mean_time = sec_to_time(int(np.mean(simulations_time_results)))
median_time = sec_to_time(int(np.median(simulations_time_results)))
min_time = sec_to_time(int(np.min(simulations_time_results)))
max_time = sec_to_time(int(np.max(simulations_time_results)))

mean_killed = int(np.mean(enemy_killed))
median_killed = int(np.median(enemy_killed))
min_killed = int(np.min(enemy_killed))
max_killed = int(np.max(enemy_killed))

print(f"Mean time: {mean_time}")
print(f"Median time: {median_time}")
print(f"Min time: {min_time}")
print(f"Max time: {max_time}")

print("-"*20)
print(f"Mean killed: {mean_killed}")
print(f"Median killed: {median_killed}")
print(f"Min killed: {min_killed}")
print(f"Max killed: {max_killed}")
