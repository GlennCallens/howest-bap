import requests
from github_authentication import get_token

url = "https://api.github.com"


def get_pbis(token, repository):
    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET", url + "/repos/glenncallens/" + repository + "/issues", headers=headers,
                                data=payload)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Failed to get issues  HTTP Status Code: {response.status_code}")
        print(response.json())


def get_pbi(token, repository, pbi_id):
    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET", url + "/repos/glenncallens/" + repository + "/issues/" + str(pbi_id),
                                headers=headers, data=payload)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Failed to get issue  HTTP Status Code: {response.status_code}")
        print(response.json())
