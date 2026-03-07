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
from aiogram.types import Message, CallbackQuery

from uuid import UUID

from ...database.requests.game import get_game_by_code
from ...database.requests.team import get_teams_in_game, update_team
from ...keyboards.author import author_dashboard
from ...keyboards.author.team_fields import team_fields
from ...keyboards.author.teams_edit import teams_edit
from ...states.author import EditTeamStates
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data.startswith("author:edit_team:"))
async def edit_team_start(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    teams = await get_teams_in_game(game.id)
    if not teams:
        await callback.answer("Нет зарегистрированных команд", show_alert=True)
        return
    await state.update_data(game_code=code)
    await safe_edit(
        callback,
        "✏️ <b>Выберите команду для редактирования:</b>",
        teams_edit(code, teams),
    )


@router.callback_query(F.data.startswith("edit_team_select:"))
async def edit_team_select(callback: CallbackQuery, state: FSMContext) -> None:
    team_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    await state.update_data(edit_team_id=team_id)
    await safe_edit(
        callback,
        "✏️ <b>Что изменить в команде?</b>",
        team_fields(team_id, data["game_code"]),
    )


@router.callback_query(F.data.startswith("team_field:"))
async def edit_team_field_select(callback: CallbackQuery, state: FSMContext) -> None:
    _, team_id, field = callback.data.split(":")
    await state.update_data(edit_team_id=team_id)
    if field == "name":
        await state.set_state(EditTeamStates.waiting_name)
        await safe_edit(callback, "✏️ Введите новое <b>название</b> команды:")
    elif field == "count":
        await state.set_state(EditTeamStates.waiting_count)
        await safe_edit(callback, "✏️ Введите новое <b>количество участников</b>:")


@router.message(EditTeamStates.waiting_name)
async def save_team_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым")
        return
    data = await state.get_data()
    await update_team(UUID(data["edit_team_id"]), name=name)
    game = await get_game_by_code(data["game_code"])
    await state.set_state(None)
    await message.answer(
        f"✅ Название команды изменено на '{esc(name)}'",
        reply_markup=author_dashboard(game.code, game.status),
    )


@router.message(EditTeamStates.waiting_count)
async def save_team_count(message: Message, state: FSMContext) -> None:
    try:
        count = int(message.text.strip())
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите положительное целое число")
        return
    data = await state.get_data()
    await update_team(UUID(data["edit_team_id"]), member_count=count)
    game = await get_game_by_code(data["game_code"])
    await state.set_state(None)
    await message.answer(
        f"✅ Количество участников изменено на {count}",
        reply_markup=author_dashboard(game.code, game.status),
    )
