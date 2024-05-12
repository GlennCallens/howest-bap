import os.path

import azure.functions as func
import logging

from dotenv import load_dotenv

from ai.import_data import import_repo
from github.download_repo import download_repo
from github.issue import get_issue, post_comment_with_solution
from github.scan_issues import scan
from ai.get_context import search
from ai.get_solution import get_solution, decide_file

load_dotenv('.env')
app = func.FunctionApp()


@app.route(route="import")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for get repository.')

    repository = req.params.get('repo')

    if not repository:
        return func.HttpResponse(
            "Invalid Request: Get repository needs 1 argument: repository name",
            status_code=400
        )

    result = download_repo(repository)
    import zipfile
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall('temp/')
    result_import = import_repo(os.path.abspath('temp/'), "index-" + repository)

    if result and result_import:
        return func.HttpResponse(
            "Import successfully",
            status_code=200
        )

    return func.HttpResponse(
        "Import failed",
        status_code=500
    )


@app.route(route="scan_projects")
def scan_projects(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for scan projects.')

    repo = req.params.get('repo')

    if not repo:
        return func.HttpResponse(
            "Invalid Request: Scan projects needs 1 argument: repository name",
            status_code=400
        )

    scan(repo)
    return func.HttpResponse(
        "Scan successfully",
        status_code=200
    )


@app.route(route="get_solution")
def get_solution(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for get solution.')

    repo = req.params.get('repo')
    issue_number = req.params.get('issue_number')

    if not repo or not issue_number:
        return func.HttpResponse(
            "Invalid Request: Get solution needs 2 arguments: repository name and issue number",
            status_code=400
        )
    question = get_issue(repo, issue_number)

    context = search(question, repo)
    file = decide_file(question, context)
    solution = get_solution(question, context[file])

    post_comment_with_solution(repo, issue_number, solution)

    return func.HttpResponse(
        "Solution added.",
        status_code=200
    )
