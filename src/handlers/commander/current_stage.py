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
from ...database.requests.actor import get_actor_by_id
from ...database.requests.stage import get_active_stage_for_team
from ...database.requests.team import count_completed_stages
from ...states import CommanderStates


router = Router()


@router.message(CommanderStates.in_game, F.text == "📍 Текущий этап")
async def current_stage(message: Message, state: FSMContext):
    data = await state.get_data()
    team_id = UUID(data["team_id"])
    stage = await get_active_stage_for_team(team_id)

    if not stage:
        done = await count_completed_stages(team_id)
        await message.answer(
            f"⏳ Ожидание следующего актёра...\nПройдено этапов: {done}"
        )
        return

    actor = await get_actor_by_id(stage.actor_id)
    text = f"📍 <b>Текущий этап</b>\n\n👤 <b>Актёр:</b> {actor.name}\n"
    if actor.location:
        text += f"📍 <b>Локация:</b> {actor.location}\n"
    if actor.description:
        text += f"📝 {actor.description}\n"

    status_labels = {
        StageStatus.ASSIGNED: "🚶 Направляйтесь к актёру",
        StageStatus.IN_PROGRESS: "🎭 Взаимодействие",
    }
    text += f"\n🔄 <b>Статус:</b> {status_labels.get(stage.status, str(stage.status))}"
    await message.answer(text)
