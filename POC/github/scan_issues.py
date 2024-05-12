import json
import logging
import os

import requests

from github.authentication import authenticate


def get_all_issues_ids(repo: str):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repo + "/issues",
                                headers=headers,
                                data=payload)

    if response.status_code == 200:
        json_response = response.json()
        return [x['number'] for x in json_response]
    else:
        logging.error(f"Failed to get issues  HTTP Status Code: {response.status_code}")
        return []


def check_if_already_entered(repo: str, issue_number: int):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = {}
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("GET",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/glenncallens/" + repo + f"/issues/{issue_number}/comments",
                                headers=headers,
                                data=payload)

    if response.status_code == 200:
        json_response = response.json()
        for comment in json_response:
            if comment['performed_via_github_app'] is not None:
                return True
        return False
    else:
        logging.error(f"Failed to get comments  HTTP Status Code: {response.status_code}")
        return []


def comment_on_issue(repo: str, issue_number: int):
    token = authenticate(os.getenv('CERT_PATH'), os.getenv('GITHUB_APP_ID'), os.getenv('GITHUB_API_URL'))

    payload = {
        "body": "Do you want me to propose code here? \n [ ✅ Yes](http://localhost:7071/api/get_solution?repo="
                + repo + "&issue_number=" + str(issue_number)
    }

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + str(token),
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.request("POST",
                                os.getenv(
                                    'GITHUB_API_URL') + "/repos/" + os.getenv(
                                    'GITHUB_USER') + "/" + repo + f"/issues/{issue_number}/comments",
                                headers=headers,
                                data=json.dumps(payload))

    if response.status_code == 201:
        return True
    else:
        logging.error(f"Failed to comment  HTTP Status Code: {response.status_code}")
        return False


def scan(repo: str):
    issues = get_all_issues_ids(repo)
    for issue in issues:
        if not check_if_already_entered(repo, issue):
            comment_on_issue(repo, issue)
