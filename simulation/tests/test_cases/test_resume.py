import pytest

from src.PFC import PFC_Sim

def test_resume_2D():
    pfc = PFC_Sim("./tests/test_files/2D_resume.yaml")
    print(pfc.config)
    assert True
