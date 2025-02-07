import os, json, urllib, pytest
import urllib.request
from core.FRSHSitesInfo import FRSHSitesInfo



@pytest.fixture()
def sitesObj():
    sitesObj = FRSHSitesInfo(dataFilePath=os.path.join(os.path.dirname(__file__), "../resources/data.json"))
    yield sitesObj
    
    
@pytest.fixture(scope="session")
def sitesInfo():
    sitesObj= FRSHSitesInfo(dataFilePath=os.path.join(os.path.dirname(__file__), "../resources/data.json"))
    sitesIterable = {site.name: site.information for site in sitesObj}
    yield sitesIterable
    
    
    
@pytest.fixture(scope="session")
def remoteSchema():
    schemaUrl: str = "https://github.com/AIAnsar1/Farasha/resources/data.schema.json"
    with urllib.request.urlopen(schemaUrl) as remotesSchema:
        schemadat = json.load(remotesSchema)
    yield schemadat