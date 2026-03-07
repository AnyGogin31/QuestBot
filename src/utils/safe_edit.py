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

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup


_NOT_MODIFIED = "message is not modified"
_CANT_EDIT = "there is no text in the message to edit"


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    *,
    answer_text: str = "",
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if _NOT_MODIFIED not in str(exc) and _CANT_EDIT not in str(exc):
            raise
    finally:
        await callback.answer(answer_text)


async def safe_edit_markup(
    callback: CallbackQuery,
    reply_markup: InlineKeyboardMarkup | None = None,
    *,
    answer_text: str = "",
) -> None:
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if _NOT_MODIFIED not in str(exc):
            raise
    finally:
        await callback.answer(answer_text)
