import time

import requests
from jwt import jwk_from_pem, JWT


def generate_jwt(path_of_cert: str, app_id: str):
    # Generate a JWT Token with our private key.
    pem = open(path_of_cert, 'rb')
    signing_key = jwk_from_pem(pem.read())

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': app_id
    }

    jwt_instance = JWT()
    return jwt_instance.encode(payload, signing_key, alg='RS256')


def get_installation_id(jwt: str, url: str):
    # Get the installation id of the app.
    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(jwt),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET", url + "/users/glenncallens/installation", headers=headers, data=payload)
    return response.json()['id']


def authenticate(path_of_cert: str, app_id: str, url: str):
    # Get the token for the app.
    jwt = generate_jwt(path_of_cert, app_id)
    installation_id = get_installation_id(jwt, url)

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(jwt),
        'X-GitHub-Api-Version': '2022-11-28'
    }
    response = requests.request("POST", url + "/app/installations/" + str(installation_id) + "/access_tokens",
                                headers=headers, data=payload)
    return response.json()['token']
