"""
    PLO-Ciwaruga

    Connection Method to Label Studio
    20/04/2020
"""

import requests
from requests import Response

def sendToLabelStudio(data: dict, apiUrl: str) -> Response:
    req = requests.post(apiUrl + "/import", json=data)

    return req