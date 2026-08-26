from __future__ import annotations

import time
from typing import Any

import requests


class JsonHttpClient:
    def __init__(self, headers: dict[str, str]) -> None:
        self.session = requests.Session()
        self.session.headers.update(headers)

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        attempts: int = 4,
        timeout: int = 40,
    ) -> Any:
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                response = self.session.get(url, params=params, timeout=timeout)

                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", "5"))
                    time.sleep(max(wait, 2))
                    continue

                if response.status_code >= 500:
                    time.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                return response.json()

            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < attempts - 1:
                    time.sleep(2 ** attempt)

        raise RuntimeError(f"Request failed after {attempts} attempts: {last_error}")
