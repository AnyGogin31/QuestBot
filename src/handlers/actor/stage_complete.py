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

from ...database.models.common import StageStatus, ActorStatus, GameStatus
from ...database.requests.actor import get_actor_by_id, set_actor_status
from ...database.requests.game import get_game_by_code
from ...database.requests.stage import get_active_stage_for_actor
from ...database.requests.team import get_team_by_id
from ...keyboards.actor import actor_confirm_complete, actor_in_game
from ...states import ActorStates
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data == "actor:stage_complete", ActorStates.in_game)
async def stage_complete_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    game = await get_game_by_code(data["game_code"])
    if game.status != GameStatus.RUNNING:
        await callback.answer("⏳ Игра ещё не запущена организатором", show_alert=True)
        return

    stage = await get_active_stage_for_actor(UUID(data["actor_id"]))
    if stage is None:
        await callback.answer("❌ Нет активного этапа", show_alert=True)
        return
    if stage.status != StageStatus.IN_PROGRESS:
        await callback.answer("⚠️ Сначала нажмите 'Команда прибыла'", show_alert=True)
        return

    team = await get_team_by_id(stage.team_id)
    await state.update_data(stage_id=str(stage.id))
    await safe_edit(
        callback,
        f"⚠️ <b>Завершить этап с командой '{esc(team.name)}'?</b>\n\n"
        f"Это действие нельзя отменить",
        actor_confirm_complete(),
    )


@router.callback_query(F.data == "actor:confirm_complete", ActorStates.in_game)
async def stage_complete_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))
    game = await get_game_by_code(data["game_code"])

    await set_actor_status(actor.id, ActorStatus.WAITING_SCORE)
    await state.set_state(ActorStates.waiting_score)

    min_s = actor.min_score if actor.min_score is not None else game.min_score
    max_s = actor.max_score if actor.max_score is not None else game.max_score
    await safe_edit(
        callback,
        f"⭐ <b>Введите баллы командой в чат</b>\n\nЦелое число от {min_s} до {max_s}:",
    )


@router.callback_query(F.data == "actor:cancel_complete", ActorStates.in_game)
async def stage_complete_cancel(callback: CallbackQuery) -> None:
    await safe_edit(callback, "↩️ Возврат к этапу.", actor_in_game())
