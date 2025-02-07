import pytest, random, string, re
from core.Farasha import farasha
from core.FRSHQueryNotify import FRSHQueryNotify
from core.FRSHQueryStatus import FRSHQueryStatus


def simpleQuery(sitesInfo: dict, site: str, username: str) -> FRSHQueryStatus:
    queryNotify = FRSHQueryNotify()
    siteData: dict = {}
    siteData[site] = sitesInfo[site]
    return farasha(username=username, siteData=siteData, queryNotify=queryNotify)[site]["status"].status



@pytest.mark.online
class TestLiveTargets():
    @pytest.mark.parametrize('site,username',[('GitLab', 'ppfeister'), ('AllMyLinks', 'blue')])
    def test_known_positives_via_message(self, sitesInfo, site, username):
        assert simpleQuery(sitesInfo=sitesInfo, site=site, username=username) is FRSHQueryStatus.CLAIMED
        
        
    @pytest.mark.parametrize('site,username',[('GitHub', 'ppfeister'),('GitHub', 'farasha'),('Docker Hub', 'ppfeister'),('Docker Hub', 'sherlock')])
    def test_known_positives_via_status_code(self, sitesInfo, site, username):
        assert simpleQuery(sitesInfo=sitesInfo, site=site, username=username) is FRSHQueryStatus.CLAIMED
        
     
    @pytest.mark.parametrize('site,username',[('Keybase', 'blue'),('devRant', 'blue')])   
    def test_known_positives_via_response_url(self, sitesInfo, site, username):
        assert simpleQuery(sitesInfo=sitesInfo, site=site, username=username) is FRSHQueryStatus.CLAIMED
        
        
    @pytest.mark.parametrize('site,random_len',[('GitLab', 255),('Codecademy', 30)])
    def test_likely_negatives_via_message(self, sitesInfo, site, random_len):
        numAttempts: int = 3
        attemptedUsernames: list[str] = []
        status: FRSHQueryStatus = FRSHQueryStatus.CLAIMED
        
        for i in range(numAttempts):
            acceptableTypes = string.ascii_letters + string.digits
            randomHandle = ''.join(random.choice(acceptableTypes) for _ in range(random_len))
            attemptedUsernames.append(randomHandle)
            status = simpleQuery(sitesInfo=sitesInfo, site=site, username=randomHandle)
            
            if status in FRSHQueryStatus.AVIALABLE:
                break
        assert status is FRSHQueryStatus.AVIALABLE, f"Could not validate available username after {numAttempts} attempts with randomly generated usernames {attemptedUsernames}."
        
    
    @pytest.mark.parametrize('site,random_len',[('GitHub', 39),('Docker Hub', 30)])
    def test_likely_negatives_via_status_code(self, sitesInfo, site, random_len):
        numAttempts: int = 3
        attemptedUsernames: list[str] = []
        status: FRSHQueryStatus = FRSHQueryStatus.CLAIMED
        
        for i in range(numAttempts):
            acceptableTypes = string.ascii_letters + string.digits
            randomHandle = ''.join(random.choice(acceptableTypes) for _ in range(random_len))
            attemptedUsernames.append(randomHandle)
            status = simpleQuery(sitesInfo=sitesInfo, site=site, username=randomHandle)
            
            if status in FRSHQueryStatus.AVIALABLE:
                break
        assert status is FRSHQueryStatus.AVIALABLE, f"Could not validate available username after {numAttempts} attempts with randomly generated usernames {attemptedUsernames}."
        
        
def test_username_illegal_regex(sitesInfo):
    site: str = 'BitBucket'
    invalidHandle: str = '*#$Y&*JRE'
    pattern = re.compile(sitesInfo[site]['regexCheck'])
    assert pattern.match(invalidHandle) is None
    assert simpleQuery(sitesInfo=sitesInfo, site=site, username=invalidHandle) is FRSHQueryStatus.ILLEGAL