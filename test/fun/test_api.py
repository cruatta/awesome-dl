import requests


def test_e2e():
    r = requests.post("http://localhost:8080/ytdl/task", json={"url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ"},
                      headers={"X-ADL-Key": "test"})
    assert r.ok is True
    uuid = r.json()["uuid"]
    r = requests.get("http://localhost:8080/task/progress/{}".format(uuid), headers={"X-ADL-Key": "test"})
    assert r.ok is True
    assert len(r.json()) == 1
    r = requests.post("http://localhost:8080/task/cancel", json={"uuid": uuid}, headers={"X-ADL-Key": "test"})
    assert r.ok is True
    r = requests.get("http://localhost:8080/task/all", headers={"X-ADL-Key": "test"})
    assert r.ok is True
    assert len(r.json()) == 1
    assert r.json()[0]["task"]["status"] == 2


def test_no_api_key():
    r = requests.get("http://localhost:8080/task/all", headers={"X-Whatever": "test"})
    assert r.ok is False


def test_get_all():
    r = requests.get("http://localhost:8080/task/all", headers={"X-ADL-Key": "test"})
    assert r.ok is True


def test_get_ytdl_formats():
    r = requests.get("http://localhost:8080/ytdl/profiles", headers={"X-ADL-Key": "test"})
    assert r.ok is True


def test_get_running():
    r = requests.get("http://localhost:8080/task/running", headers={"X-ADL-Key": "test"})
    assert r.ok is True


def test_get_health():
    r = requests.get("http://localhost:8080/health", headers={"X-ADL-Key": "test"})
    assert r.ok is True
    assert r.json()["version"] is not ""