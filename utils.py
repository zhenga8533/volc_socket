import requests


def get_player_head(player: str) -> str:
    """
    Get the player head image URL from the player's username.

    :param player: The player's username.
    """

    url = f'https://mc-heads.net/avatar/{player}'
    return url

def post_request(url: str, json: dict) -> requests.Response:
    """
    Send a POST request to a URL with a JSON payload.

    :param url: The URL to send the request to.
    :param json: The JSON payload to send.
    """

    return requests.post(url, json=json)
