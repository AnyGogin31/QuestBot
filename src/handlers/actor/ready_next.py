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
from aiogram.types import CallbackQuery

from uuid import UUID

from ..notification import notify_team_new_actor, notify_actor_incoming_team
from ...database.models.common import ActorStatus, GameStatus
from ...database.requests.actor import get_actor_by_id, set_actor_status
from ...database.requests.game import get_game_by_code
from ...database.requests.stage import find_and_assign_waiting_team
from ...keyboards.actor import actor_in_game
from ...states import ActorStates
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data == "actor:ready_next", ActorStates.in_game)
async def ready_next(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()

    game = await get_game_by_code(data["game_code"])
    if game.status != GameStatus.RUNNING:
        await callback.answer("⏳ Игра ещё не запущена организатором", show_alert=True)
        return

    actor = await get_actor_by_id(UUID(data["actor_id"]))
    if actor.status == ActorStatus.BUSY:
        await callback.answer(
            "⚠️ Вы сейчас обслуживаете команду. Сначала завершите этап",
            show_alert=True,
        )
        return

    waiting_team = await find_and_assign_waiting_team(actor.game_id, actor.id)

    if waiting_team:
        actor_refreshed = await get_actor_by_id(actor.id)
        await notify_team_new_actor(bot, waiting_team, actor_refreshed)
        await notify_actor_incoming_team(bot, actor_refreshed, waiting_team)
        await safe_edit(
            callback,
            f"👥 <b>Вам назначена новая команда: '{esc(waiting_team.name)}'!</b>",
            actor_in_game(),
        )
    else:
        await set_actor_status(actor.id, ActorStatus.FREE)
        await safe_edit(
            callback,
            "⏳ <b>Ожидание следующей команды...</b>\n"
            "Как только команда освободится вам придёт уведомление",
            actor_in_game(),
        )
