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

from aiogram.fsm.storage.base import StorageKey

from .storage import get_storage, get_bot_id
from .logging import get_logger

_logger = get_logger(__name__)


async def set_user_state(
    user_telegram_id: int, state_str: str, extra_data: dict | None = None
):
    storage = get_storage()
    bot_id = get_bot_id()
    if storage is None or bot_id is None:
        _logger.warning(
            "storage_holder not initialised; cannot set state for user %s",
            user_telegram_id,
        )
        return
    key = StorageKey(bot_id=bot_id, chat_id=user_telegram_id, user_id=user_telegram_id)
    await storage.set_state(key=key, state=state_str)
    if extra_data:
        current = await storage.get_data(key=key)
        current.update(extra_data)
        await storage.set_data(key=key, data=current)
