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

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from uuid import UUID

from ..notification import (
    notify_team_new_actor,
    notify_actor_incoming_team,
    notify_team_finished,
)
from ...database.requests.actor import get_actor_by_id
from ...database.requests.game import get_game_by_code
from ...database.requests.stage import (
    complete_stage,
    find_and_assign_next_actor,
    has_unvisited_actors,
)
from ...database.requests.team import get_team_by_id, mark_team_finished
from ...keyboards.actor import actor_in_game
from ...states import ActorStates


router = Router()


@router.message(ActorStates.waiting_score)
async def enter_score(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))
    game = await get_game_by_code(data["game_code"])

    min_s = actor.min_score if actor.min_score is not None else game.min_score
    max_s = actor.max_score if actor.max_score is not None else game.max_score

    try:
        score = int(message.text.strip())
        if not (min_s <= score <= max_s):
            raise ValueError
    except ValueError:
        await message.answer(f"❌ Введите целое число от {min_s} до {max_s}")
        return

    team_id = await complete_stage(UUID(data["stage_id"]), score)
    team = await get_team_by_id(team_id)
    next_actor = await find_and_assign_next_actor(game.id, team.id)

    if next_actor:
        await notify_team_new_actor(bot, team, next_actor)
        await notify_actor_incoming_team(bot, next_actor, team)
    elif not await has_unvisited_actors(game.id, team.id):
        await mark_team_finished(team.id)
        team = await get_team_by_id(team.id)
        await notify_team_finished(bot, team)

    await state.set_state(ActorStates.in_game)
    await message.answer(
        f"✅ <b>Баллы выставлены: {score}</b>",
        reply_markup=actor_in_game(),
    )
