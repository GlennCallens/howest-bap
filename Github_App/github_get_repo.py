import requests
from github_authentication import get_token

url = "https://api.github.com"


def get_contents(token, repository_name):
    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET",
                                url + "/repos/glenncallens/" + repository_name + "/zipball/main",
                                headers=headers,
                                data=payload)

    if response.status_code == 200:
        with open('../temp.zip', 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        print("success")
    else:
        print(f"Failed to download repository  HTTP Status Code: {response.status_code}")

