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

from aiogram.utils.keyboard import InlineKeyboardBuilder

from typing import List

from ...database.models import GameModel
from ...database.models.common import GameStatus


_STATUS_LABELS = {
    GameStatus.CREATED: "📝 создана",
    GameStatus.PREPARED: "✅ готова",
    GameStatus.RUNNING: "▶️ идёт",
    GameStatus.FINISHED: "🏁 завершена",
    GameStatus.CANCELLED: "❌ отменена",
}


def games_list(games: List[GameModel]):
    builder = InlineKeyboardBuilder()
    for game in games:
        title = game.title or f"Игра {game.code}"
        label = _STATUS_LABELS.get(game.status, str(game.status))
        builder.button(
            text=f"{title} [{label}]", callback_data=f"author:open:{game.code}"
        )
    builder.button(text="🔙 Назад", callback_data="author:back_main")
    builder.adjust(1)
    return builder.as_markup()
