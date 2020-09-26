
import pytest

def test_ok():
    assert True

    with pytest.raises(Exception):
        raise Exception()
    
