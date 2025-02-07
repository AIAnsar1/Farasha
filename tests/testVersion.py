import os, core
from farashaInteractives import FRSHInteractives

def test_versioning() -> None:
    assert core.__version__ in FRSHInteractives.runCli("--version")
    found: list = FRSHInteractives.flyFarashaForFilesWith(r'__version__ *= *')
    expected: list = [os.path.normpath("core/__init__.py")]
    assert sorted(found) == sorted(expected)