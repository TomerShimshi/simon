import json
import urllib.error
from unittest.mock import MagicMock, patch

from simon.kv_store import FileKeyValueStore, InMemoryKeyValueStore, UpstashKeyValueStore

DEFAULT = {"sessions": []}


def test_file_store_returns_default_when_missing(tmp_path):
    store = FileKeyValueStore(tmp_path)
    assert store.load("progress", DEFAULT) == DEFAULT


def test_file_store_round_trips(tmp_path):
    store = FileKeyValueStore(tmp_path)
    store.save("progress", {"sessions": [1, 2, 3]})
    assert store.load("progress", DEFAULT) == {"sessions": [1, 2, 3]}


def test_file_store_falls_back_to_default_on_corrupt_json(tmp_path):
    (tmp_path / "progress.json").write_text("not json", encoding="utf-8")
    store = FileKeyValueStore(tmp_path)
    assert store.load("progress", DEFAULT) == DEFAULT


def test_file_store_uses_separate_files_per_key(tmp_path):
    store = FileKeyValueStore(tmp_path)
    store.save("a", {"x": 1})
    store.save("b", {"x": 2})
    assert store.load("a", DEFAULT) == {"x": 1}
    assert store.load("b", DEFAULT) == {"x": 2}


def test_in_memory_store_returns_default_when_missing():
    store = InMemoryKeyValueStore()
    assert store.load("progress", DEFAULT) == DEFAULT


def test_in_memory_store_round_trips():
    store = InMemoryKeyValueStore()
    store.save("progress", {"sessions": [1]})
    assert store.load("progress", DEFAULT) == {"sessions": [1]}


def test_in_memory_store_returned_value_is_a_copy_not_a_reference():
    store = InMemoryKeyValueStore()
    store.save("progress", {"sessions": []})
    loaded = store.load("progress", DEFAULT)
    loaded["sessions"].append("mutated")
    assert store.load("progress", DEFAULT) == {"sessions": []}


def _mock_response(payload: dict) -> MagicMock:
    cm = MagicMock()
    cm.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
    return cm


def test_upstash_store_load_parses_the_result_field():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", return_value=_mock_response({"result": '{"sessions": [1]}'})):
        assert store.load("progress", DEFAULT) == {"sessions": [1]}


def test_upstash_store_load_returns_default_when_key_missing():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", return_value=_mock_response({"result": None})):
        assert store.load("progress", DEFAULT) == DEFAULT


def test_upstash_store_load_returns_default_on_network_error():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("boom")):
        assert store.load("progress", DEFAULT) == DEFAULT


def test_upstash_store_save_posts_json_encoded_body():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", return_value=_mock_response({"result": "OK"})) as mock_open:
        store.save("progress", {"sessions": [1]})
    request = mock_open.call_args[0][0]
    assert request.full_url == "https://example.upstash.io/set/progress"
    assert json.loads(request.data) == {"sessions": [1]}
    assert request.get_header("Authorization") == "Bearer token"


def test_upstash_store_save_does_not_raise_on_network_error():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("boom")):
        store.save("progress", {"sessions": [1]})  # must not raise
