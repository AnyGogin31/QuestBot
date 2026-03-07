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
from aiogram.types import Message, CallbackQuery

from ..utils.logging import get_logger


_logger = get_logger(__name__)


_ERR_TEXT = "⚠️ Произошла внутренняя ошибка. Попробуйте повторить позже"


class ErrorLoggerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as exc:
            _logger.exception(
                "Необработанное исключение для user_id=%s: %s",
                getattr(getattr(event, "from_user", None), "id", "?"),
                exc,
            )
            if isinstance(event, Message):
                await event.answer(_ERR_TEXT)
            elif isinstance(event, CallbackQuery):
                try:
                    await event.answer(_ERR_TEXT, show_alert=True)
                except Exception:
                    pass
            return None
