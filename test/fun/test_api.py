import requests


def test_no_api_key():
    r = requests.get("http://localhost:8080/task/queue", headers={"X-Whatever": "test"})
    assert r.ok is False


def test_get_queue():
    r = requests.get("http://localhost:8080/task/queue", headers={"X-ADL-Key": "test"})
    assert r.ok is True


def test_get_ytdl_formats():
    r = requests.get("http://localhost:8080/ytdl/formats", headers={"X-ADL-Key": "test"})
    assert r.ok is True


def test_get_running():
    r = requests.get("http://localhost:8080/task/running", headers={"X-ADL-Key": "test"})
    assert r.ok is True
