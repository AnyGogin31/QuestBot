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

from ...database.models.common import StageStatus, ActorStatus
from ...database.requests.actor import get_actor_by_id, set_actor_status
from ...database.requests.stage import get_active_stage_for_actor
from ...database.requests.team import get_team_by_id
from ...keyboards.actor import actor_confirm_complete
from ...states import ActorStates
from ...utils.escape import esc

router = Router()


@router.message(ActorStates.in_game, F.text == "✅ Этап завершён")
async def stage_complete_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    stage = await get_active_stage_for_actor(UUID(data["actor_id"]))

    if stage is None:
        await message.answer("❌ Нет активного этапа")
        return
    if stage.status != StageStatus.IN_PROGRESS:
        await message.answer("⚠️ Сначала нажмите 'Команда прибыла'")
        return

    team = await get_team_by_id(stage.team_id)
    await state.update_data(stage_id=str(stage.id))
    await message.answer(
        f"⚠️ <b>Завершить этап с командой '{esc(team.name)}'?</b>\n\nЭто действие нельзя отменить",
        reply_markup=actor_confirm_complete(),
    )


@router.callback_query(F.data == "actor_confirm_complete", ActorStates.in_game)
async def stage_complete_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))
    await set_actor_status(actor.id, ActorStatus.WAITING_SCORE)
    await state.set_state(ActorStates.waiting_score)

    from ...database.requests.game import get_game_by_code

    game = await get_game_by_code(data["game_code"])
    min_s = actor.min_score if actor.min_score is not None else game.min_score
    max_s = actor.max_score if actor.max_score is not None else game.max_score
    await callback.message.answer(
        f"⭐ <b>Введите баллы</b>\n\nЦелое число от {min_s} до {max_s}:"
    )


@router.callback_query(F.data == "actor_cancel_complete", ActorStates.in_game)
async def stage_complete_cancel(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer("Возврат к этапу")
