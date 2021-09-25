from src.collatinus_words.common import Common
import pytest


@pytest.fixture()
def common():
    return Common()


def test_read_model(common: Common):
    assert len(common.read_model(__file__)) == 12
