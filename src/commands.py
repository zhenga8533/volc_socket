import time
from concurrent.futures import ThreadPoolExecutor
from utils import *
import json


def process_event(data: dict, key: str) -> dict:
    """
    Process event data and return the averages for each event.

    :param data: The event data to process.
    :param key: The key to access the event data.
    """

    event_data = data.get(key, [])
    parsed_data = []
    events = {}
    total = 0

    # Add up total time for each event
    for event in event_data:
        # Check if the event is valid
        [name, timestamp] = event
        if name not in events:
            events[name] = {
                'count': 0,
                'time': 0
            }
        
        # Check if the event has already ended
        time_left = timestamp - time.time()
        if time_left > 0:
            parsed_data.append(event)
            events[name]['count'] += 1
            events[name]['time'] += time_left
            total += 1
    
    data[key] = parsed_data
    
    # Determine averages for each event
    return_data = {'command': key, 'total': total, 'events': {}}
    for name in events:
        if events[name]['count'] == 0:
            continue

        # Calculate the percentage of the event
        percentage = events[name]['count'] / total * 100
        return_data['events'][name] = {
            'time': events[name]['time'] / events[name]['count'],
            'percentage': percentage
        }
    
    return return_data

def send_webhook(player: str, message: str, url: str) -> None:
    """
    Send a webhook message to a Discord channel.

    :param player: The player's username.
    :param message: The message to send.
    :param url: The webhook URL to send the message to.
    """

    avatar_url = get_player_head(player)

    payload = {
        'content': message,
        'username': player,
        'avatar_url': avatar_url
    }

    with ThreadPoolExecutor() as executor:
        executor.submit(post_request, url, payload)
