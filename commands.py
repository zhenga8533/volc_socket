import time


def process_event(data):
    events = {}
    data_copy = data.copy()

    for event in data_copy:
        [name, timestamp] = event
        if name not in events:
            events[name] = {
                'count': 0,
                'time': 0
            }
        
        time_left = timestamp + 20 * 60 - time.time()
        if time_left < 0:
            data.remove(event)
            continue
        
        events[name]['count'] += 1
        events[name]['time'] += time_left
    
    return events
