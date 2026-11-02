import pytest

import const


def test_get_env_returns_value(monkeypatch):
    monkeypatch.setenv('CST_TEST_KEY', 'value')

    assert const._get_env('CST_TEST_KEY') == 'value'


@pytest.mark.parametrize('value', [None, ''])
def test_get_env_rejects_missing_or_empty(monkeypatch, value):
    if value is None:
        monkeypatch.delenv('CST_TEST_KEY', raising=False)
    else:
        monkeypatch.setenv('CST_TEST_KEY', value)

    with pytest.raises(KeyError):
        const._get_env('CST_TEST_KEY')
