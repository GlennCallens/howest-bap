import os

import requests

from github.authentication import authenticate


def download_repo(repository_name: str):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repository_name + "/zipball/main",
                                headers=headers,
                                data=payload)

    if response.status_code == 200:
        with open('temp.zip', 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return True
    else:
        print(f"Failed to download repository  HTTP Status Code: {response.status_code}")
        return False
