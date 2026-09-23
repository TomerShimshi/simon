import json
import urllib.error
from unittest.mock import MagicMock, patch

from simon.kv_store import (
    FileKeyValueStore,
    InMemoryKeyValueStore,
    NamespacedKeyValueStore,
    UpstashKeyValueStore,
    get_default_store,
)

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


def test_file_store_treats_colon_as_a_subdirectory(tmp_path):
    """Regression test: a raw "namespace:key.json" filename is a broken
    Windows Alternate Data Stream name, not a real file."""
    store = FileKeyValueStore(tmp_path)
    store.save("efraim:progress_v1", {"sessions": [1]})
    assert (tmp_path / "efraim" / "progress_v1.json").is_file()
    assert store.load("efraim:progress_v1", DEFAULT) == {"sessions": [1]}


def test_file_store_namespaced_keys_do_not_collide(tmp_path):
    store = FileKeyValueStore(tmp_path)
    store.save("efraim:progress_v1", {"sessions": ["efraim's"]})
    store.save("tomer:progress_v1", {"sessions": ["tomer's"]})
    assert store.load("efraim:progress_v1", DEFAULT) == {"sessions": ["efraim's"]}
    assert store.load("tomer:progress_v1", DEFAULT) == {"sessions": ["tomer's"]}


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


def _http_error(code: int, reason: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://example.upstash.io/get/progress",
        code=code,
        msg=reason,
        hdrs=None,
        fp=MagicMock(read=lambda: b'{"error":"denied"}'),
    )


def test_upstash_store_load_returns_default_on_http_error_eg_bad_token():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", side_effect=_http_error(401, "Unauthorized")):
        assert store.load("progress", DEFAULT) == DEFAULT


def test_upstash_store_save_does_not_raise_on_http_error():
    store = UpstashKeyValueStore("https://example.upstash.io", "token")
    with patch("urllib.request.urlopen", side_effect=_http_error(403, "Forbidden")):
        store.save("progress", {"sessions": [1]})  # must not raise


def test_get_default_store_picks_upstash_when_env_vars_set(monkeypatch):
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://example.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "sometoken")
    assert isinstance(get_default_store(), UpstashKeyValueStore)


def test_get_default_store_falls_back_to_file_when_unset(monkeypatch):
    monkeypatch.delenv("UPSTASH_REDIS_REST_URL", raising=False)
    monkeypatch.delenv("UPSTASH_REDIS_REST_TOKEN", raising=False)
    assert isinstance(get_default_store(), FileKeyValueStore)


def test_get_default_store_strips_accidental_surrounding_quotes(monkeypatch):
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", '"https://example.upstash.io"')
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "'sometoken'")
    store = get_default_store()
    assert isinstance(store, UpstashKeyValueStore)
    assert store._url == "https://example.upstash.io"
    assert store._token == "sometoken"


def test_get_default_store_strips_whitespace(monkeypatch):
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "  https://example.upstash.io  \n")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "  sometoken  \n")
    store = get_default_store()
    assert store._url == "https://example.upstash.io"
    assert store._token == "sometoken"


def test_namespaced_store_prefixes_keys_on_the_inner_store():
    inner = InMemoryKeyValueStore()
    namespaced = NamespacedKeyValueStore(inner, "efraim")
    namespaced.save("progress_v1", {"sessions": [1]})
    assert inner.load("efraim:progress_v1", {}) == {"sessions": [1]}
    assert namespaced.load("progress_v1", {}) == {"sessions": [1]}


def test_namespaced_store_isolates_different_namespaces():
    inner = InMemoryKeyValueStore()
    efraim = NamespacedKeyValueStore(inner, "efraim")
    tomer = NamespacedKeyValueStore(inner, "tomer")

    efraim.save("progress_v1", {"sessions": ["efraim's"]})
    tomer.save("progress_v1", {"sessions": ["tomer's"]})

    assert efraim.load("progress_v1", {}) == {"sessions": ["efraim's"]}
    assert tomer.load("progress_v1", {}) == {"sessions": ["tomer's"]}
