from datetime import time


def sec_to_time(time_in_sec):
    hour = time_in_sec // (60 * 60)  # Convert time to minutes
    minutes = time_in_sec % (60 * 60) // 60  # Convert time to minutes
    seconds = time_in_sec % (60 * 60) % 60  # Remaining seconds
    return time(hour=hour, minute=int(minutes), second=int(seconds))
