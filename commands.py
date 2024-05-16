import time
import requests
from concurrent.futures import ThreadPoolExecutor
from utils import *


def process_event(data, key):
    event_data = data.get(key, [])
    events = {}
    data_copy = event_data.copy()
    total = 0

    # Add up total time for each event
    for event in data_copy:
        [name, timestamp] = event
        if name not in events:
            events[name] = {
                'count': 0,
                'time': 0
            }
        
        time_left = timestamp + 20 * 60 - time.time()
        if time_left < 0:
            event_data.remove(event)
            continue
        
        events[name]['count'] += 1
        events[name]['time'] += time_left
        total += 1
    
    # Determine averages for each event
    return_data = {'command': key, 'total': total, 'events': {}}
    for name in events:
        percentage = events[name]['count'] / total * 100
        return_data['events'][name] = {
            'time': events[name]['time'] / events[name]['count'],
            'percentage': percentage
        }
    
    return return_data

def send_webhook(player, message, url):
    avatar_url = get_player_head(player)

    payload = {
        'content': message,
        'username': player,
        'avatar_url': avatar_url
    }

    with ThreadPoolExecutor() as executor:
        executor.submit(post_request, url, payload)

if __name__ == '__main__':
    test = 'https://discord.com/api/webhooks/1240695018575106079/K1NyC56k7rxGdlGIHaNa7Gk62_Sq3mU8ffgPARU65VCjHMoc80tRynP_F1pUnwZi80Ec'
    ping = '<@&1137127306134036480>'
    msg = ' ⚑ The 2x Powder event starts in 20 seconds! This is a passive event! It\'s happening everywhere in the Crystal Hollows!'
    send_webhook('Volcaronitee', ping + msg, test)
