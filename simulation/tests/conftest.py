import os
import pytest

@pytest.fixture(autouse=True)
def test_cleanup():
    """
    Deletes files produced by tests. Exception for Trajectory which handles the
    deletion in test test_trajectory in test_analyses.py

    """
    yield
    files = [
        "pfc.log",
        "pfc.h5",
    ]
    for file in files:
        if os.path.exists(file):
            os.remove(file)
