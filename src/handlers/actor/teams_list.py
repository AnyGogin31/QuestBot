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

from ...database.models.common import TeamStatus, ActorStatus
from ...database.requests.actor import get_actor_by_id
from ...database.requests.team import get_teams_in_game, count_completed_stages
from ...keyboards.actor.actor_active import actor_active
from ...keyboards.actor.actor_after_score import actor_after_score
from ...keyboards.actor.actor_waiting import actor_waiting
from ...states import ActorStates
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

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


def _back(actor_status: ActorStatus):
    if actor_status == ActorStatus.BUSY:
        return actor_active()
    if actor_status == ActorStatus.WAITING_SCORE:
        return actor_after_score()
    return actor_waiting()


@router.callback_query(F.data == "actor:teams_list", ActorStates.in_game)
async def teams_list(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data["actor_id"]))
    teams = await get_teams_in_game(actor.game_id)

    lines = []
    for team in teams:
        done = await count_completed_stages(team.id)
        em = _STATUS_EMOJI.get(team.status, "❓")
        label = _STATUS_LABELS.get(team.status, str(team.status))
        lines.append(
            f"{em} <b>{esc(team.name)}</b> - {team.member_count} чел."
            f" | этапов: {done} | {label}"
        )

    await safe_edit(
        callback,
        "📋 <b>Список команд:</b>\n\n" + ("\n".join(lines) or "Команд пока нет"),
        _back(actor.status),
    )
