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

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from uuid import UUID

from ...database.requests.game import get_game_by_code
from ...database.requests.team import get_team_by_commander, create_team
from ...keyboards.commander import commander_lobby
from ...states import JoinCommanderStates, CommanderStates
from ...utils.escape import esc

router = Router()


@router.message(JoinCommanderStates.waiting_team_name)
async def step_team_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым")
        return
    await state.update_data(team_name=name)
    await state.set_state(JoinCommanderStates.waiting_member_count)
    await message.answer("Сколько человек в команде? (число или /skip):")


@router.message(JoinCommanderStates.waiting_member_count)
async def step_member_count(message: Message, state: FSMContext):
    if message.text.strip() == "/skip":
        count = 1
    else:
        try:
            count = int(message.text.strip())
            if count < 1:
                raise ValueError
        except ValueError:
            await message.answer("❌ Введите положительное целое число")
            return

    data = await state.get_data()
    user_id = UUID(data["user_id"])
    game_id = UUID(data["game_id"])

    game = await get_game_by_code(data["game_code"])
    existing = await get_team_by_commander(user_id)

    if existing and existing.game_id == game_id:
        await state.set_state(CommanderStates.lobby)
        await state.update_data(team_id=str(existing.id))
        await message.answer(
            "ℹ️ Вы уже зарегистрированы в этой игре", reply_markup=commander_lobby()
        )
        return

    team = await create_team(
        game_id=game_id,
        commander_id=user_id,
        name=data["team_name"],
        member_count=count,
    )
    await state.set_state(CommanderStates.lobby)
    await state.update_data(team_id=str(team.id))
    await message.answer(
        f"✅ <b>Команда зарегистрирована!</b>\n\n"
        f"🏷 <b>Название:</b> {esc(data['team_name'])}\n"
        f"👤 <b>Участников:</b> {count}\n"
        f"🎮 <b>Игра:</b> {esc(game.title) or game.code}\n\n"
        f"Нажмите <b>'Готов к игре'</b>, когда будете готовы",
        reply_markup=commander_lobby(),
    )
