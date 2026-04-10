import logging
import math
import traceback
import datetime as dt

import requests

from typing import Iterable
from zoneinfo import ZoneInfo

import re


def str_join(iterable: Iterable, splitter: str = ",") -> str:
    """Convert elements of iterable to a string and join them."""
    return splitter.join(map(str, iterable))


class Telegram:
    __MD2_ESCAPE_RE = re.compile(r'([_*\[\]()~`>#+\-=|{}.!])')
    __MAX_LEN = 4000 # Telegram API limit is 4096

    @classmethod
    def escape_md2(cls, text: str) -> str:
        return cls.__MD2_ESCAPE_RE.sub(r'\\\1', str(text))

    @staticmethod
    def _make_error_msg(e) -> str:
        """Build MarkdownV2 safe error message."""
        text = "".join(
            traceback.format_exception(type(e), e, e.__traceback__, chain=True)
        )
        text = text.replace("```", "'''")
        msg = f"""\n\n```python\n{text}\n```"""

        return msg

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

        self.message_thread_id =  getattr(self.config, "message_thread_id", None)
        self.app_name = self.escape_md2(self.config.name)
        self.url = f"https://api.telegram.org/bot{self.config.token}/sendMessage"
        self.tz = self.config.tz

        self.session = requests.Session()


    def _make_base_msg(self, text: str) -> str:
        """Build base message. And place text message between `` quotes."""
        now = dt.datetime.now(ZoneInfo(self.tz)).strftime("%Y-%m-%d %H:%M:%S")
        safe_now = self.escape_md2(now)
        safe_text = self.escape_md2(text)

        msg = f"App: `{self.app_name}`\nTime: `{safe_now}`\n\n{safe_text}"
        return msg

    def _post_md2(self, _msg, message_thread_id=None):
        """Send MarkdownV2 text to Telegram channel."""
        if message_thread_id is None:
            message_thread_id = self.message_thread_id
        
        try:
            numb_batches = math.ceil(len(_msg) / self.__MAX_LEN)
            for i in range(numb_batches):
                
                if numb_batches == 1:
                    msg = _msg
            
                else:
                    chunk = _msg[i * self.__MAX_LEN: (i + 1) * self.__MAX_LEN]
                    if chunk.endswith("\\"):
                        chunk = chunk[:-1]

                    msg = (
                        f"{i}/{numb_batches}\n\n" 
                        + 
                        + "\n\n...split..."
                     )

                data = {
                    "chat_id": self.config.chat_id,
                    "text": msg,
                    "parse_mode": "MarkdownV2",
                }

                if message_thread_id:
                    data["message_thread_id"] = message_thread_id

                response = self.session.post(url=self.url, data=data, timeout=10)
                response.raise_for_status()

                payload = response.json()
                if not payload.get("ok"):
                    self.logger.error(f"Telegram API error: {payload}\non message: {msg}")

                self.logger.debug(payload)

        except Exception:
            self.logger.error(f"Failed POST TG error, on message: {_msg}", exc_info=True)

    def post(self, message: str, *, message_thread_id: int | None = None):
        msg = self._make_base_msg(message)
        self._post_md2(msg, message_thread_id=message_thread_id)

    def post_error(
        self,
        message: str,
        error: Exception | None = None,
        *,
        message_thread_id=None,
    ):
        """Log error and post exception to Telegram."""

        self.logger.error(message, exc_info=bool(error))
        base_msg = self._make_base_msg(message)
        error_msg = self._make_error_msg(error) if error else ""

        msg = base_msg + error_msg
        self._post_md2(msg, message_thread_id=message_thread_id)

