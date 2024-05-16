import requests


def get_player_head(player):
    url = f'https://mc-heads.net/avatar/{player}'
    return url

def post_request(url, json):
    return requests.post(url, json=json)
