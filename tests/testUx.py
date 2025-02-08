import pytest
from core import farasha, FRSHInteractiveSubproccessError
from farashaInteractives import FRSHInteractives

def test_remove_nsfw(sites_obj):
    nsfw_target: str = 'Pornhub'
    assert nsfw_target in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites()
    assert nsfw_target not in {site.name: site.information for site in sites_obj}


@pytest.mark.parametrize('nsfwsites', [['Pornhub'], ['Pornhub', 'Xvideos']])
def test_nsfw_explicit_selection(sites_obj, nsfwsites):
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites(do_not_remove=nsfwsites)
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
        assert 'Motherless' not in {site.name: site.information for site in sites_obj}

def test_wildcard_username_expansion():
    assert farasha.check_for_parameter('test{?}test') is True
    assert farasha.check_for_parameter('test{.}test') is False
    assert farasha.check_for_parameter('test{}test') is False
    assert farasha.check_for_parameter('testtest') is False
    assert farasha.check_for_parameter('test{?test') is False
    assert farasha.check_for_parameter('test?}test') is False
    assert farasha.multiple_usernames('test{?}test') == ["test_test" , "test-test" , "test.test"]


@pytest.mark.parametrize('cliargs', ['','--site urghrtuight --egiotr','--'])
def test_no_usernames_provided(cliargs):
    with pytest.raises(FRSHInteractiveSubproccessError, match=r"error: the following arguments are required: USERNAMES"):
        FRSHInteractives.run_cli(cliargs)