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

from aiogram import Router, F
from aiogram.types import CallbackQuery

from .main_menu import _dashboard_text
from ...database.requests.game import (
    set_commanders_closed,
    set_actors_closed,
)
from ...keyboards.author import author_dashboard
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data.startswith("author:reg_cmd:"))
async def toggle_commanders(callback: CallbackQuery) -> None:
    _, _, action, code = callback.data.split(":")
    closed = action == "close"
    game = await set_commanders_closed(code, closed)
    if game is None:
        await callback.answer("Игра не найдена", show_alert=True)
        return
    label = "закрыт 🔒" if closed else "открыт 🔓"
    await safe_edit(
        callback,
        _dashboard_text(game),
        author_dashboard(
            game.code, game.status, game.commanders_closed, game.actors_closed
        ),
        answer_text=f"Набор команд {label}",
    )


@router.callback_query(F.data.startswith("author:reg_act:"))
async def toggle_actors(callback: CallbackQuery) -> None:
    _, _, action, code = callback.data.split(":")
    closed = action == "close"
    game = await set_actors_closed(code, closed)
    if game is None:
        await callback.answer("Игра не найдена", show_alert=True)
        return
    label = "закрыт 🔒" if closed else "открыт 🔓"
    await safe_edit(
        callback,
        _dashboard_text(game),
        author_dashboard(
            game.code, game.status, game.commanders_closed, game.actors_closed
        ),
        answer_text=f"Набор актёров {label}",
    )
