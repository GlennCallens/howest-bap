import json
import logging
import os

import requests

from github.authentication import authenticate


def get_issue(repo: str, issue_number: str):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repo + f"/issues/{issue_number}",
                                headers=headers,
                                data=payload)

    if response.status_code == 200:
        json_response = response.json()
        return json_response['title']
    else:
        logging.error(f"Failed to get issue  HTTP Status Code: {response.status_code}")
        return []


def post_comment_with_solution(repo: str, issue_number: str, comment: str):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = json.dumps({
        "body": "```" + comment + "`` \n Import into project? \n [Yes](http://localhost:7071/api/commit_solution?repo="
                + repo + ")`"
    })
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("POST",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repo + f"/issues/{issue_number}/comments",
                                headers=headers,
                                data=payload)

    if response.status_code == 201:
        return True
    else:
        logging.error(f"Failed to post comment  HTTP Status Code: {response.status_code}")
        return False
