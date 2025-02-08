import pytest, random, string, re
from core.Farasha import farasha
from core.FRSHQueryNotify import FRSHQueryNotify
from core.FRSHQueryStatus import FRSHQueryStatus


def simple_query(sites_info: dict, site: str, username: str) -> FRSHQueryStatus:
    query_notify = FRSHQueryNotify()
    site_data: dict = {}
    site_data[site] = sites_info[site]
    return farasha(username=username,site_data=site_data,query_notify=query_notify)[site]['status'].status


@pytest.mark.online
class TestLiveTargets:
    @pytest.mark.parametrize('site,username',[('GitLab', 'ppfeister'),('AllMyLinks', 'blue')])
    def test_known_positives_via_message(self, sites_info, site, username):
        assert simple_query(sites_info=sites_info, site=site, username=username) is FRSHQueryStatus.CLAIMED



    @pytest.mark.parametrize('site,username',[('GitHub', 'ppfeister'),('GitHub', 'sherlock-project'), ('Docker Hub', 'ppfeister'), ('Docker Hub', 'sherlock') ])
    def test_known_positives_via_status_code(self, sites_info, site, username):
        assert simple_query(sites_info=sites_info, site=site, username=username) is FRSHQueryStatus.CLAIMED



    @pytest.mark.parametrize('site,username',[('Keybase', 'blue'), ('devRant', 'blue')])
    def test_known_positives_via_response_url(self, sites_info, site, username):
        assert simple_query(sites_info=sites_info, site=site, username=username) is FRSHQueryStatus.CLAIMED



    @pytest.mark.parametrize('site,random_len',[ ('GitLab', 255), ('Codecademy', 30)])
    def test_likely_negatives_via_message(self, sites_info, site, random_len):
        num_attempts: int = 3
        attempted_usernames: list[str] = []
        status: FRSHQueryStatus = FRSHQueryStatus.CLAIMED
        for i in range(num_attempts):
            acceptable_types = string.ascii_letters + string.digits
            random_handle = ''.join(random.choice(acceptable_types) for _ in range (random_len))
            attempted_usernames.append(random_handle)
            status = simple_query(sites_info=sites_info, site=site, username=random_handle)
            if status is FRSHQueryStatus.AVAILABLE:
                break
        assert status is FRSHQueryStatus.AVAILABLE, f"[ INFO ]: Could not validate available username after {num_attempts} attempts with randomly generated usernames {attempted_usernames}."



    @pytest.mark.parametrize('site,random_len',[('GitHub', 39),('Docker Hub', 30)])
    def test_likely_negatives_via_status_code(self, sites_info, site, random_len):
        num_attempts: int = 3
        attempted_usernames: list[str] = []
        status: FRSHQueryStatus = FRSHQueryStatus.CLAIMED
        for i in range(num_attempts):
            acceptable_types = string.ascii_letters + string.digits
            random_handle = ''.join(random.choice(acceptable_types) for _ in range (random_len))
            attempted_usernames.append(random_handle)
            status = simple_query(sites_info=sites_info, site=site, username=random_handle)
            if status is FRSHQueryStatus.AVAILABLE:
                break
        assert status is FRSHQueryStatus.AVAILABLE, f"Could not validate available username after {num_attempts} attempts with randomly generated usernames {attempted_usernames}."


def test_username_illegal_regex(sites_info):
    site: str = 'BitBucket'
    invalid_handle: str = '*#$Y&*JRE'
    pattern = re.compile(sites_info[site]['regexCheck'])
    assert pattern.match(invalid_handle) is None
    assert simple_query(sites_info=sites_info, site=site, username=invalid_handle) is FRSHQueryStatus.ILLEGAL