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

from ...database.models.common import GameStatus


def author_dashboard(game_code: str, status: GameStatus):
    builder = InlineKeyboardBuilder()
    if status in (GameStatus.CREATED, GameStatus.PREPARED):
        builder.button(
            text="🚀 Запустить игру", callback_data=f"author:start_game:{game_code}"
        )
    if status == GameStatus.RUNNING:
        builder.button(
            text="📊 Статус игры", callback_data=f"author:game_status:{game_code}"
        )
        builder.button(
            text="🏁 Завершить игру", callback_data=f"author:finish_game:{game_code}"
        )
    if status != GameStatus.FINISHED:
        builder.button(
            text="✏️ Изменить команду", callback_data=f"author:edit_team:{game_code}"
        )
        builder.button(
            text="✏️ Изменить актёра", callback_data=f"author:edit_actor:{game_code}"
        )
    builder.button(
        text="👥 Участники", callback_data=f"author:participants:{game_code}"
    )
    builder.button(text="🔙 Мои игры", callback_data="author:my_games")
    builder.adjust(1)
    return builder.as_markup()
