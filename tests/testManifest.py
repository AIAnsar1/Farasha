import os, json, pytest
from jsonschema import validate


def textValidateManifestAgainstLocalSchema():
    jsonRealtive: str = "../resources/data.json"
    schemaRealtive: str = "../resources/data.schema.json"
    jsonPath: str = os.path.join(os.path.dirname(__file__), jsonRealtive)
    schemaPath: str = os.path.join(os.path.dirname(__file__), schemaRealtive)
    
    with open(jsonPath, 'r') as f:
        jsondat = json.load(f)
    with open(schemaPath, 'r') as f:
        schemadat = json.load(f)
    validate(instance=jsondat, schema=schemadat)



def testValidateManifestAgainstRemoteSchema(remotesSchema):
    jsonRealtive: str = "../resources/data.json"
    jsonPath: str = os.path.join(os.path.dirname(__file__), jsonRealtive)
    
    with open(jsonRealtive, 'r') as f:
        jsondat = json.load(f)
    validate(instance=jsondat, schema=remotesSchema)
    

@pytest.mark.parametrize("target_name,target_expected_err_type", [('GitHub', 'status_code'),('GitLab', 'message')])
def testSiteListInterability(sitesInfo, targetName, targetExcpectedErrType):
    assert sitesInfo[targetName]['errorType'] == targetExcpectedErrType



















