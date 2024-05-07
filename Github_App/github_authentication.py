# First generate a JWT token with our private key.
import os
import time

import requests
from jwt import jwk_from_pem, JWT

url = "https://api.github.com"
app_id = 889013


def generate_jwt():
    # Generate a JWT Token with our private key.
    pem = open(os.getenv('CERT_PATH'), 'rb')
    signing_key = jwk_from_pem(pem.read())

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': app_id
    }

    jwt_instance = JWT()
    return jwt_instance.encode(payload, signing_key, alg='RS256')


def get_installation_id():
    # Get the installation id of the app.
    jwt = generate_jwt()

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(jwt),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET", url + "/users/glenncallens/installation", headers=headers, data=payload)
    return response.json()['id']


def get_token():
    # Get the token for the app.
    installation_id = get_installation_id()
    jwt = generate_jwt()

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(jwt),
        'X-GitHub-Api-Version': '2022-11-28'
    }
    response = requests.request("POST", url + "/app/installations/" + str(installation_id) + "/access_tokens",
                                headers=headers, data=payload)
    return response.json()['token']
