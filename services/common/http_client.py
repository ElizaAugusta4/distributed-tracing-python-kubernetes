from __future__ import annotations

import os
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_DEFAULT_CONNECT_TIMEOUT = float(os.getenv("HTTP_CONNECT_TIMEOUT", "0.5"))
_DEFAULT_READ_TIMEOUT = float(os.getenv("HTTP_READ_TIMEOUT", "2.0"))
DEFAULT_TIMEOUT = (_DEFAULT_CONNECT_TIMEOUT, _DEFAULT_READ_TIMEOUT)

_RETRY_TOTAL = int(os.getenv("HTTP_RETRY_TOTAL", "2"))
_RETRY_BACKOFF = float(os.getenv("HTTP_RETRY_BACKOFF", "0.2"))

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is not None:
        return _session

    retry = Retry(
        total=_RETRY_TOTAL,
        connect=_RETRY_TOTAL,
        read=_RETRY_TOTAL,
        status=_RETRY_TOTAL,
        backoff_factor=_RETRY_BACKOFF,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)

    s = requests.Session()
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    _session = s
    return s


def http_request(method: str, url: str, *, timeout: tuple[float, float] | None = None, **kwargs: Any) -> requests.Response:
    """HTTP request with safe defaults.

    - Always sets a timeout (connect, read)
    - Retries idempotent methods on transient failures (5xx, timeouts)
    """

    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    return _get_session().request(method, url, timeout=timeout, **kwargs)
