import json

from sampleorder.json_store import JsonFileStore


def test_load_returns_empty_list_when_file_missing(tmp_path):
    store = JsonFileStore(tmp_path / "missing.json")

    assert store.load() == []


def test_save_then_load_round_trip(tmp_path):
    store = JsonFileStore(tmp_path / "data.json")
    records = [{"id": "A-1", "value": 1}, {"id": "A-2", "value": 2}]

    store.save(records)

    assert store.load() == records


def test_save_writes_valid_json_file_on_disk(tmp_path):
    path = tmp_path / "data.json"
    store = JsonFileStore(path)

    store.save([{"id": "A-1"}])

    assert path.exists()
    with path.open(encoding="utf-8") as f:
        assert json.load(f) == [{"id": "A-1"}]


def test_save_creates_missing_parent_directories(tmp_path):
    path = tmp_path / "nested" / "dir" / "data.json"
    store = JsonFileStore(path)

    store.save([{"id": "A-1"}])

    assert path.exists()
    assert store.load() == [{"id": "A-1"}]


def test_save_overwrites_previous_content(tmp_path):
    store = JsonFileStore(tmp_path / "data.json")

    store.save([{"id": "A-1"}])
    store.save([{"id": "B-1"}])

    assert store.load() == [{"id": "B-1"}]
