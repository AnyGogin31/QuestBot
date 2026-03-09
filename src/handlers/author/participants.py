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
from aiogram.types import CallbackQuery

from ...database.models.common import TeamStatus, ActorStatus
from ...database.requests.actor import get_actors_in_game
from ...database.requests.game import get_game_by_code
from ...database.requests.team import get_teams_in_game
from ...keyboards.author import author_dashboard
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


_TEAM_STATUS = {
    TeamStatus.IDLE: "⏳ ожидает",
    TeamStatus.EN_ROUTE: "🚶 готова",
    TeamStatus.AT_ACTOR: "🎭 у актёра",
    TeamStatus.FINISHED: "🏁 финиш",
}
_ACTOR_STATUS = {
    ActorStatus.FREE: "✅ свободен",
    ActorStatus.BUSY: "🔄 занят",
    ActorStatus.WAITING_SCORE: "⏳ выставляет баллы",
}


@router.callback_query(F.data.startswith("author:participants:"))
async def participants(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    teams = await get_teams_in_game(game.id)
    actors = await get_actors_in_game(game.id)

    text = f"👥 <b>Участники игры {game.code}</b>\n\n"
    text += f"<b>Команды ({len(teams)}):</b>\n"
    for t in teams:
        label = _TEAM_STATUS.get(t.status, str(t.status))
        text += f"  {label} - {esc(t.name)} ({t.member_count} чел.)\n"

    text += f"\n<b>Актёры ({len(actors)}):</b>\n"
    for a in actors:
        label = _ACTOR_STATUS.get(a.status, str(a.status))
        loc = f" [{esc(a.location)}]" if a.location else ""
        mn = a.min_score if a.min_score is not None else game.min_score
        mx = a.max_score if a.max_score is not None else game.max_score
        score_range = (
            f" ({mn}-{mx})"
            if (a.min_score is not None or a.max_score is not None)
            else ""
        )
        text += f"  {label} - {esc(a.name)}{loc}{score_range}\n"

    await safe_edit(
        callback,
        text,
        author_dashboard(code, game.status, game.commanders_closed, game.actors_closed),
    )
