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

from ...database.models.common import StageStatus, GameStatus
from ...database.requests.game import get_game_by_code
from ...database.requests.stage import get_active_stage_for_actor, mark_team_arrived
from ...keyboards.actor.actor_active import actor_active
from ...states import ActorStates
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data == "actor:team_arrived", ActorStates.in_game)
async def team_arrived(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    game = await get_game_by_code(data["game_code"])
    if game.status != GameStatus.RUNNING:
        await callback.answer("⏳ Игра ещё не запущена организатором", show_alert=True)
        return

    stage = await get_active_stage_for_actor(UUID(data["actor_id"]))
    if stage is None:
        await callback.answer("⏳ Вам ещё не назначена команда", show_alert=True)
        return
    if stage.status != StageStatus.ASSIGNED:
        await callback.answer("ℹ️ Команда уже отмечена как прибывшая", show_alert=True)
        return

    await mark_team_arrived(stage.id)
    await safe_edit(
        callback,
        "✅ <b>Команда отмечена как прибывшая</b>\n\n"
        "После взаимодействия нажмите 'Этап завершён'",
        actor_active(),
    )
