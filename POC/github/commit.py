import base64
import json
import os

import requests
from dotenv import load_dotenv

from POC.github.authentication import authenticate

load_dotenv('.env')


def get_last_commit(repository: str) -> str:
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    request = requests.request("GET", os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repository + f"/contents/Data/Repository.cs", headers=headers)

    if request.status_code != 200:
        raise Exception("Error getting last commit", request.status_code, request.json())
    return request.json()['sha']


def create_commit(repository: str, message: str, content: str):

    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }


    payload = json.dumps({
        "message": message,
        "content": content,
        "sha": get_last_commit(repository),
        "branch": "test-workspace"
    })

    response = requests.request("PUT", os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repository +
                                f"/contents/Data/Repository.cs", headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Error creating commit", response.status_code, response.json())

    return response.json()
