#  QuestBot
#  Copyright (C) 2026 AnyGogin31
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.

from aiogram import BaseMiddleware
from aiogram.types import Message

from collections import defaultdict

from time import monotonic


_PERIOD = 1.0
_MAX_CALLS = 3


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, period=_PERIOD, max_calls=_MAX_CALLS):
        self._period = period
        self._max_calls = max_calls
        self._calls = defaultdict(list)

    async def __call__(self, handler, event, data):
        if not isinstance(event, Message):
            return await handler(event, data)

        uid = event.from_user.id
        now = monotonic()
        window = self._calls[uid]

        self._calls[uid] = [t for t in window if now - t < self._period]

        if len(self._calls[uid]) >= self._max_calls:
            await event.answer("⏳ Слишком много запросов. Подождите секунду")
            return None

        self._calls[uid].append(now)
        return await handler(event, data)
