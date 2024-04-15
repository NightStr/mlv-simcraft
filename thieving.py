import random
import decimal
from typing import NamedTuple

from tqdm import tqdm

from core import sec_to_time


class SimResult(NamedTuple):
    time: int
    money_earned: int


class SimConfig(NamedTuple):
    health_regeneration_interval: int  # in seconds
    health_regeneration_amount: int
    max_health: int
    steal_interval: decimal.Decimal  # in seconds
    steal_success_chance: float
    min_damage: int
    max_damage: int
    min_gold: int
    max_gold: int


def sim(config: SimConfig) -> SimResult:
    # Variables
    current_health = config.max_health
    gold_earn = 0
    time = 0

    while current_health > 0 and time < 60 * 60 * 8:
        # Attempt to steal every 3 seconds
        if time % config.steal_interval == 0:
            if random.random() > config.steal_success_chance:
                # Failed steal attempt, take damage and get stunned
                damage = random.randint(config.min_damage, config.max_damage)
                current_health -= damage

                # Check if health drops below zero
                if current_health <= 0:
                    break

                # Stunned for 3 seconds
                time += decimal.Decimal('3.0')
            else:
                gold_earn += random.randint(config.min_gold, config.max_gold)

        # Health regeneration every 8 seconds
        if time % config.health_regeneration_interval == 0:
            current_health = min(current_health + config.health_regeneration_amount, config.max_health)

        # Increment time
        time += decimal.Decimal('0.1')
    return SimResult(time, gold_earn)


if __name__ == '__main__':
    config = SimConfig(
        health_regeneration_interval=8,  # in seconds
        health_regeneration_amount=8,
        max_health=720,
        steal_interval=decimal.Decimal('2.6'),  # in seconds
        steal_success_chance=0.9733,
        min_damage=0,
        max_damage=78,
        min_gold=0,
        max_gold=1,
    )
    sims = []
    for _ in tqdm(range(5_000), desc="Simulations"):
        sims.append(sim(config))

    sims_seconds = [s.time for s in sims]
    sims_money_earned = [s.money_earned for s in sims]

    mean_time = sec_to_time(int(sum(sims_seconds) / len(sims_seconds)))
    mean_money_earned = int(sum(sims_money_earned) / len(sims_money_earned))

    min_mean_time = sec_to_time(int(sum(sorted(sims_seconds)[:100]) / 100))
    min_money_earned = int(sum(sorted(sims_money_earned)[:100]) / 100)

    max_mean_time = sec_to_time(int(sum(list(reversed(sorted(sims_seconds)))[:100]) / 100))
    max_money_earned = int(sum(list(reversed(sorted(sims_money_earned)))[:100]) / 100)

    print(f"Mean time: {mean_time}")
    print(f"Max mean time: {max_mean_time}")
    print(f"Min mean time: {min_mean_time}")
    print("-"*20)
    print(f"Mean money earned: {mean_money_earned}")
    print(f"Max money earned: {max_money_earned}")
    print(f"Min money earned: {min_money_earned}")
