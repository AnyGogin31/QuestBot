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
from ...states import AuthorStates
from ...states.author import EditTeamStates
from ...utils.escape import esc

router = Router()


@router.message(AuthorStates.dashboard, F.text == "✏️ Изменить команду")
async def edit_team_start(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game = await get_game_by_code(data["game_code"])
    teams = await get_teams_in_game(game.id)
    if not teams:
        await message.answer("Нет зарегистрированных команд")
        return
    await state.set_state(EditTeamStates.select_team)
    await message.answer(
        "Выберите команду для редактирования:", reply_markup=teams_edit(teams)
    )


@router.callback_query(F.data.startswith("edit_team:"), EditTeamStates.select_team)
async def edit_team_select(callback: CallbackQuery, state: FSMContext) -> None:
    team_id = callback.data.split(":", 1)[1]
    await state.update_data(edit_team_id=team_id)
    await state.set_state(EditTeamStates.select_field)
    await callback.message.edit_reply_markup(reply_markup=team_fields(team_id))


@router.callback_query(F.data.startswith("team_field:"), EditTeamStates.select_field)
async def edit_team_field_select(callback: CallbackQuery, state: FSMContext) -> None:
    _, team_id, field = callback.data.split(":")
    await state.update_data(edit_team_field=field)
    await callback.message.delete()
    if field == "name":
        await state.set_state(EditTeamStates.waiting_name)
        await callback.message.answer("Введите новое название команды:")
    elif field == "count":
        await state.set_state(EditTeamStates.waiting_count)
        await callback.message.answer("Введите новое количество участников:")


@router.message(EditTeamStates.waiting_name)
async def edit_team_save_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым")
        return
    data = await state.get_data()
    await update_team(UUID(data["edit_team_id"]), name=name)
    await state.set_state(AuthorStates.dashboard)
    game = await get_game_by_code(data["game_code"])
    await message.answer(
        f"✅ Название команды изменено на '{esc(name)}'",
        reply_markup=author_dashboard(game.status),
    )


@router.message(EditTeamStates.waiting_count)
async def edit_team_save_count(message: Message, state: FSMContext) -> None:
    try:
        count = int(message.text.strip())
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите положительное целое число")
        return
    data = await state.get_data()
    await update_team(UUID(data["edit_team_id"]), member_count=count)
    await state.set_state(AuthorStates.dashboard)
    game = await get_game_by_code(data["game_code"])
    await message.answer(
        f"✅ Количество участников изменено на {count}",
        reply_markup=author_dashboard(game.status),
    )


@router.callback_query(F.data == "edit_cancel")
async def edit_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await callback.message.delete()
    await state.set_state(AuthorStates.dashboard)
    if data.get("game_code"):
        game = await get_game_by_code(data["game_code"])
        await callback.message.answer(
            "Редактирование отменено", reply_markup=author_dashboard(game.status)
        )
