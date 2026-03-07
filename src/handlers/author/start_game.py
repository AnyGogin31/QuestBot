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
from aiogram.types import CallbackQuery

from ..notification import notify_team_new_actor, notify_actor_incoming_team
from ...database.models.common import GameStatus
from ...database.requests.actor import get_free_actors_in_game
from ...database.requests.game import get_game_by_code, start_game
from ...database.requests.stage import find_and_assign_next_actor
from ...database.requests.team import get_ready_teams
from ...keyboards.author import author_dashboard
from ...utils.escape import esc

router = Router()


@router.callback_query(F.data.startswith("author:start_game:"))
async def do_start_game(callback: CallbackQuery, bot: Bot) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)

    if game.status not in (GameStatus.CREATED, GameStatus.PREPARED):
        await callback.answer("❌ Игра уже запущена или завершена", show_alert=True)
        return

    ready_teams = await get_ready_teams(game.id)
    ready_actors = await get_free_actors_in_game(game.id)

    if not ready_teams:
        await callback.answer("❌ Нет готовых команд", show_alert=True)
        return
    if not ready_actors:
        await callback.answer("❌ Нет готовых актёров", show_alert=True)
        return

    game = await start_game(code)
    assignments = []
    for team in ready_teams:
        actor = await find_and_assign_next_actor(game.id, team.id)
        if actor:
            assignments.append((team, actor))

    title = esc(game.title) or f"Игра {game.code}"
    await callback.message.edit_text(
        f"🚀 <b>Игра запущена!</b>\n\n"
        f"📛 {title}\n"
        f"✅ Команд в игре: {len(ready_teams)}\n"
        f"🎭 Актёров в игре: {len(ready_actors)}\n"
        f"📌 Назначено этапов: {len(assignments)}",
        reply_markup=author_dashboard(code, game.status),
    )

    for team, actor in assignments:
        await notify_team_new_actor(bot, team, actor)
        await notify_actor_incoming_team(bot, actor, team)
