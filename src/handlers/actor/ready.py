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

from ...database.models.common import ActorStatus
from ...database.requests.actor import set_actor_status
from ...keyboards.actor import actor_in_game
from ...states import ActorStates


router = Router()


@router.message(ActorStates.lobby, F.text == "✅ Готов к игре")
async def ready(message: Message, state: FSMContext):
    data = await state.get_data()
    await set_actor_status(UUID(data['actor_id']), ActorStatus.FREE)
    await state.set_state(ActorStates.in_game)
    await message.answer(
        "✅ <b>Готов к игре!</b>\n\nОжидайте назначения команды от организатора",
        reply_markup=actor_in_game(),
    )
