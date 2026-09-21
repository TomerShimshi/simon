"""Storage backend abstraction for the app's small JSON progress records.

Render's free web service has no persistent disk -- its filesystem resets
on every restart/redeploy, which would otherwise wipe progress history each
time the app is updated. `get_default_store()` picks an Upstash Redis-backed
store (survives redeploys) when the UPSTASH_REDIS_REST_URL/TOKEN env vars
are set, and falls back to local JSON files otherwise -- so `python main.py`
still works offline with no external account needed for local development.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Protocol

from simon.storage_paths import storage_dir as _local_storage_dir

REQUEST_TIMEOUT_S = 5


class KeyValueStore(Protocol):
    def load(self, key: str, default: dict) -> dict: ...
    def save(self, key: str, data: dict) -> None: ...


class FileKeyValueStore:
    """One JSON file per key in a local directory. Not durable on Render's
    free tier (ephemeral filesystem) -- used for local desktop development
    and as the fallback when no remote store is configured."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def _path(self, key: str) -> Path:
        return self._directory / f"{key}.json"

    def load(self, key: str, default: dict) -> dict:
        path = self._path(key)
        if not path.is_file():
            return json.loads(json.dumps(default))
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return json.loads(json.dumps(default))

    def save(self, key: str, data: dict) -> None:
        self._path(key).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )


class InMemoryKeyValueStore:
    """Pure in-memory store, no filesystem I/O -- used by tests so store
    behavior is verified hermetically and fast."""

    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def load(self, key: str, default: dict) -> dict:
        return json.loads(json.dumps(self._data.get(key, default)))

    def save(self, key: str, data: dict) -> None:
        self._data[key] = json.loads(json.dumps(data))


class UpstashKeyValueStore:
    """Stores each key as a value in an Upstash Redis database via its REST
    API -- the only one of these that survives a Render redeploy. Read/write
    failures (network hiccup, misconfigured credentials) degrade gracefully
    to an empty/unsaved record rather than crashing a game session; a
    caregiver losing one session's stats is far better than the app
    breaking mid-game for a stroke-recovery patient."""

    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._token = token

    def _request(self, method: str, path: str, body: bytes | None = None) -> dict:
        req = urllib.request.Request(
            f"{self._url}/{path}",
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self._token}"},
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read())

    def load(self, key: str, default: dict) -> dict:
        try:
            response = self._request("GET", f"get/{key}")
        except (urllib.error.URLError, OSError, TimeoutError, ValueError):
            return json.loads(json.dumps(default))

        result = response.get("result")
        if result is None:
            return json.loads(json.dumps(default))
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return json.loads(json.dumps(default))

    def save(self, key: str, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        try:
            self._request("POST", f"set/{key}", body=payload)
        except (urllib.error.URLError, OSError, TimeoutError, ValueError):
            pass  # best-effort -- the in-progress session still has the data in memory


def get_default_store() -> KeyValueStore:
    url = os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    if url and token:
        return UpstashKeyValueStore(url, token)
    return FileKeyValueStore(_local_storage_dir())
