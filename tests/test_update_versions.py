import pytest
from update import is_newer


@pytest.mark.parametrize("remote,current,expected", [
    ("v1.18.0", "1.18.0-rc.1", True),
    ("v1.18.0-rc.2", "1.18.0-rc.1", True),
    ("v1.18.0-rc.1", "1.18.0", False),
    ("v1.18.0-rc.1", "1.18.0-dev", True),
    ("v1.18.0-rc.1", "1.18.0-rc.1", False),
    ("v1.17.4", "1.18.0-rc.1", False),
    ("v1.19.0-dev", "1.18.0", True),
    ("bad", "1.18.0", False),
])
def test_release_order(remote, current, expected):
    assert is_newer(remote, current) is expected
