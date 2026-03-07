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
from aiogram.types import Message

from uuid import UUID

from ...database.models.common import StageStatus
from ...database.requests.stage import get_active_stage_for_actor, mark_team_arrived
from ...keyboards.actor import actor_in_game
from ...states import ActorStates


router = Router()


@router.message(ActorStates.in_game, F.text == "🏁 Команда прибыла")
async def team_arrived(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    stage = await get_active_stage_for_actor(UUID(data["actor_id"]))

    if stage is None:
        await message.answer("⏳ Вам ещё не назначена команда. Ожидайте")
        return
    if stage.status != StageStatus.ASSIGNED:
        await message.answer("ℹ️ Команда уже отмечена как прибывшая")
        return

    await mark_team_arrived(stage.id)
    await message.answer(
        "✅ <b>Команда отмечена как прибывшая.</b>\n\nПосле взаимодействия нажмите 'Этап завершён'",
        reply_markup=actor_in_game(),
    )
