import os, json, urllib, pytest
import urllib.request
from core.FRSHSitesInfo import FRSHSitesInformation


@pytest.fixture()
def sites_obj():
    sites_obj = FRSHSitesInformation(data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock_project/resources/data.json"))
    yield sites_obj

@pytest.fixture(scope="session")
def sites_info():
    sites_obj = FRSHSitesInformation(data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock_project/resources/data.json"))
    sites_iterable = {site.name: site.information for site in sites_obj}
    yield sites_iterable

@pytest.fixture(scope="session")
def remote_schema():
    schema_url: str = 'https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.schema.json'
    with urllib.request.urlopen(schema_url) as remoteschema:
        schemadat = json.load(remoteschema)
    yield schemadat