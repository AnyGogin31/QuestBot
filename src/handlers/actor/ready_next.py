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

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from uuid import UUID

from ..notification import notify_team_new_actor, notify_actor_incoming_team
from ...database.models.common import ActorStatus
from ...database.requests.actor import get_actor_by_id, set_actor_status
from ...database.requests.stage import find_and_assign_waiting_team
from ...keyboards.actor import actor_in_game
from ...states import ActorStates


router = Router()


@router.message(ActorStates.in_game, F.text == "➡️ Готов к следующей команде")
async def ready_next(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))

    if actor.status == ActorStatus.BUSY:
        await message.answer("⚠️ Вы сейчас обслуживаете команду. Сначала завершите этап")
        return

    waiting_team = await find_and_assign_waiting_team(actor.game_id, actor.id)

    if waiting_team:
        actor_refreshed = await get_actor_by_id(actor.id)
        await notify_team_new_actor(bot, waiting_team, actor_refreshed)
        await notify_actor_incoming_team(bot, actor_refreshed, waiting_team)
        await message.answer(
            f"👥 <b>Вам назначена новая команда: '{waiting_team.name}'!</b>",
            reply_markup=actor_in_game(),
        )
    else:
        await set_actor_status(actor.id, ActorStatus.FREE)
        await message.answer(
            "⏳ <b>Ожидание следующей команды...</b>\n"
            "Как только команда освободится вам придёт уведомление",
            reply_markup=actor_in_game(),
        )
