#  Copyright 2024 The Meatie Authors. All rights reserved.
#  Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
from json import JSONDecodeError
from typing import Any, Callable, Optional

import httpx

from meatie.error import ParseResponseError, ResponseError
from meatie.types import Response as BaseResponse


class Response(BaseResponse):
    """The sync response implementation using httpx."""

    def __init__(
        self,
        response: httpx.Response,
        get_json: Optional[Callable[[httpx.Response], Any]] = None,
        get_text: Optional[Callable[[httpx.Response], str]] = None,
    ) -> None:
        self.response = response
        if get_json is not None:
            self.get_json = get_json  # type: ignore[assignment]
        if get_text is not None:
            self.get_text = get_text  # type: ignore[assignment]

    @property
    def status(self) -> int:
        return self.response.status_code

    def read(self) -> bytes:
        try:
            return self.response.content
        except Exception as exc:
            raise ResponseError(self) from exc

    def text(self) -> str:
        try:
            return self.get_text(self.response)
        except Exception as exc:
            raise ResponseError(self) from exc

    def json(self) -> Any:
        try:
            return self.get_json(self.response)
        except JSONDecodeError as exc:
            text = self.text()
            raise ParseResponseError(text, self) from exc
        except Exception as exc:
            raise ResponseError(self) from exc

    @classmethod
    def get_json(cls, response: httpx.Response) -> Any:
        return response.json()

    @classmethod
    def get_text(cls, response: httpx.Response) -> str:
        return response.text
