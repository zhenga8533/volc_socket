import time


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

def send_webhook(data, url):
    pass
