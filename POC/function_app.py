import os.path

import azure.functions as func
import logging

from dotenv import load_dotenv

from ai.import_data import import_repo
from github.download_repo import download_repo

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
