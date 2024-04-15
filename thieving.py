from datetime import time
import random
import decimal

from core import sec_to_time


def sim(i):
    print(f"Start iteration: {i}")
    # Constants
    health_regeneration_interval = 8  # in seconds
    health_regeneration_amount = 8
    max_health = 720
    steal_interval = decimal.Decimal('2.6')  # in seconds
    steal_success_chance = 0.9733  # 72%
    min_damage = 0
    max_damage = 78

    # Variables
    current_health = max_health
    time = 0

    while current_health > 0 and time < 60 * 60 * 8:
        # Attempt to steal every 3 seconds
        if time % steal_interval == 0:
            if random.random() > steal_success_chance:
                # Failed steal attempt, take damage and get stunned
                damage = random.randint(min_damage, max_damage)
                current_health -= damage

                # Check if health drops below zero
                if current_health <= 0:
                    break

                # Stunned for 3 seconds
                time += decimal.Decimal('3.0')

        # Health regeneration every 8 seconds
        if time % health_regeneration_interval == 0:
            current_health = min(current_health + health_regeneration_amount, max_health)

        # Increment time
        time += decimal.Decimal('0.1')

    # time_elapsed = time // 60  # Convert time to minutes
    # time_elapsed_seconds = time % 60  # Remaining seconds

    return time


sims_seconds = [sim(i) for i in range(5000)]

mean_time = sec_to_time(int(sum(sims_seconds) / len(sims_seconds)))
min_mean_time = sec_to_time(int(sum(sorted(sims_seconds)[:100]) / 100))
max_mean_time = sec_to_time(int(sum(list(reversed(sorted(sims_seconds)))[:100]) / 100))

print(f"Mean time: {mean_time}")
print(f"Max mean time: {max_mean_time}")
print(f"Min mean time: {min_mean_time}")
