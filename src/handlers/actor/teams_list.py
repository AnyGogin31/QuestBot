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

from ...database.models.common import TeamStatus
from ...database.requests.actor import get_actor_by_id
from ...database.requests.team import get_teams_in_game, count_completed_stages
from ...states import ActorStates
from ...utils.escape import esc

router = Router()


_STATUS_EMOJI = {
    TeamStatus.IDLE: "⏳",
    TeamStatus.EN_ROUTE: "🚶",
    TeamStatus.AT_ACTOR: "🎭",
    TeamStatus.FINISHED: "🏁",
}
_STATUS_LABELS = {
    TeamStatus.IDLE: "ожидает",
    TeamStatus.EN_ROUTE: "в пути",
    TeamStatus.AT_ACTOR: "у актёра",
    TeamStatus.FINISHED: "финиш",
}


@router.message(ActorStates.in_game, F.text == "📋 Список команд")
async def teams_list(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))
    teams = await get_teams_in_game(actor.game_id)

    lines = []
    for team in teams:
        done = await count_completed_stages(team.id)
        em = _STATUS_EMOJI.get(team.status, "❓")
        label = _STATUS_LABELS.get(team.status, str(team.status))
        lines.append(
            f"{em} <b>{esc(team.name)}</b> - {team.member_count} чел. | этапов: {done} | {label}"
        )

    await message.answer("📋 <b>Список команд:</b>\n\n" + "\n".join(lines))
