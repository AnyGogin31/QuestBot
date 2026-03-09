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
from ...database.requests.game import get_game_by_code
from ...database.requests.team import get_teams_in_game, delete_team
from ...keyboards.author import author_dashboard
from ...keyboards.author.confirm_delete_team import confirm_delete_team
from ...keyboards.author.teams_edit import teams_edit
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data.startswith("author:del_team:"))
async def del_team_start(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    teams = await get_teams_in_game(game.id)
    if not teams:
        await callback.answer("Нет команд для удаления", show_alert=True)
        return
    await state.update_data(game_code=code)
    await safe_edit(
        callback,
        "🗑 <b>Выберите команду для удаления:</b>",
        teams_edit(code, teams, action="delete"),
    )


@router.callback_query(F.data.startswith("del_team_select:"))
async def del_team_select(callback: CallbackQuery, state: FSMContext) -> None:
    team_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    await safe_edit(
        callback,
        "⚠️ <b>Удалить команду?</b>\n\nВсе этапы команды также будут удалены",
        confirm_delete_team(team_id, data["game_code"]),
    )


@router.callback_query(F.data.startswith("del_team_confirm:"))
async def del_team_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    team_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    ok = await delete_team(UUID(team_id))
    game = await get_game_by_code(data["game_code"])
    if not ok:
        await callback.answer("Команда не найдена", show_alert=True)
        return
    await safe_edit(
        callback,
        _dashboard_text(game),
        author_dashboard(
            game.code, game.status, game.commanders_closed, game.actors_closed
        ),
        answer_text="✅ Команда удалена",
    )
