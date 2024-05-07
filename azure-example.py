import os

from dotenv import load_dotenv

from Github_App.github_authentication import get_token
from Github_App.github_get_repo import get_contents
from Azure.import_data import run

load_dotenv('.env')


def import_data():
    # Download data from GitHub
    get_contents(get_token(), 'test_Sonar')
    # Unzip data
    import zipfile
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall('temp/')

    run(os.path.abspath('temp/'))



