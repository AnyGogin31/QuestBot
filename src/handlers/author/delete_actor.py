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
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from uuid import UUID

from .main_menu import _dashboard_text
from ...database.requests.actor import get_actors_in_game, delete_actor
from ...database.requests.game import get_game_by_code
from ...keyboards.author import author_dashboard
from ...keyboards.author.actors_edit import actors_edit
from ...keyboards.author.confirm_delete_actor import confirm_delete_actor
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data.startswith("author:del_actor:"))
async def del_actor_start(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    actors = await get_actors_in_game(game.id)
    if not actors:
        await callback.answer("Нет актёров для удаления", show_alert=True)
        return
    await state.update_data(game_code=code)
    await safe_edit(
        callback,
        "🗑 <b>Выберите актёра для удаления:</b>",
        actors_edit(code, actors, action="delete"),
    )


@router.callback_query(F.data.startswith("del_actor_select:"))
async def del_actor_select(callback: CallbackQuery, state: FSMContext) -> None:
    actor_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    await safe_edit(
        callback,
        "⚠️ <b>Удалить актёра?</b>\n\nВсе связанные этапы также будут удалены",
        confirm_delete_actor(actor_id, data["game_code"]),
    )


@router.callback_query(F.data.startswith("del_actor_confirm:"))
async def del_actor_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    actor_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    ok = await delete_actor(UUID(actor_id))
    game = await get_game_by_code(data["game_code"])
    if not ok:
        await callback.answer("Актёр не найден", show_alert=True)
        return
    await safe_edit(
        callback,
        _dashboard_text(game),
        author_dashboard(
            game.code, game.status, game.commanders_closed, game.actors_closed
        ),
        answer_text="✅ Актёр удалён",
    )
