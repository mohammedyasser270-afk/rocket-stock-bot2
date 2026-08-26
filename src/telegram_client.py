from __future__ import annotations

import requests


class TelegramClient:
    def __init__(self, token: str, chat_id: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id

    def send(self, message: str) -> None:
        for chunk in self._split(message, 3900):
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": chunk,
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            response.raise_for_status()

    @staticmethod
    def _split(message: str, maximum: int) -> list[str]:
        if len(message) <= maximum:
            return [message]

        chunks: list[str] = []
        current = ""

        for line in message.splitlines(keepends=True):
            if current and len(current) + len(line) > maximum:
                chunks.append(current.rstrip())
                current = ""
            current += line

        if current:
            chunks.append(current.rstrip())

        return chunks
