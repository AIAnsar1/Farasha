import pytest
from core import farasha, FRSHInteractiveSubproccessError
from farashaInteractives import FRSHInteractives

def test_remove_nsfw(sitesObj):
    nsfwTarget: str = 'Pornhub'
    assert nsfwTarget in {site.name: site.information for site in sitesObj}
    sitesObj.removeNsfwSites()
    assert nsfwTarget not in {site.name: site.information for site in sitesObj}
    
    
    
@pytest.mark.parametrize('nsfwsites', [['Pornhub'],['Pornhub', 'Xvideos']])
def test_nsfw_explicit_selection(sitesObj, nsfwSites):
    for site in nsfwSites:
        assert site in {site.name: site.information for site in sitesObj}
    sitesObj.removeNsfwSites(doNotRemove=nsfwSites)
    for site in nsfwSites:
        assert site in {site.name: site.information for site in sitesObj}
        assert 'Motherless' not in {site.name: site.information for site in sitesObj}
        
        
def test_wildcard_username_expansion():
    assert farasha.checkForParameter('test{?}test') is True
    assert farasha.checkForParameter('test{.}test') is False
    assert farasha.checkForParameter('test{}test') is False
    assert farasha.checkForParameter('testtest') is False
    assert farasha.checkForParameter('test{?test') is False
    assert farasha.checkForParameter('test?}test') is False
    assert farasha.checkForParameter('test{?}test') == ["test_test" , "test-test" , "test.test"]
    
    
    
@pytest.mark.parametrize('cliargs', [ '', '--site urghrtuight --egiotr', '--'])
def test_no_usernames_provided(cliArgs):
     with pytest.raises(FRSHInteractiveSubproccessError, match=r"error: the following arguments are required: USERNAMES"):
        FRSHInteractives.runCli(cliArgs)