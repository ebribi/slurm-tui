import pytest
from slurm_cli.parsing import parse_duration, parse_mem_mb

def test_duration():
    assert parse_duration("00:01:29") == 89
    assert parse_duration("00:00:00") == 0
    assert parse_duration("00:00.002") == 0.002
    assert parse_duration("00:00.576") == 0.576
    assert parse_duration("1-02:03:04") == 93784
    assert parse_duration("") is None
    assert parse_duration("UNLIMITED") is None

def test_duration_bad():
    with pytest.raises(ValueError):
        parse_duration("abc")
    with pytest.raises(ValueError):
        parse_duration("1:2:3:4")

def test_mem():
    assert parse_mem_mb("4G") == 4096
    assert parse_mem_mb("50M") == 50
    assert parse_mem_mb("440K") == 0.4296875
    assert parse_mem_mb("2120K") == 2.0703125
    assert parse_mem_mb("") is None

def test_mem_bad():
    with pytest.raises(ValueError):
        parse_mem_mb("12X")
