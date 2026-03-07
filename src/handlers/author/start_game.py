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

from ..notification import notify_team_new_actor, notify_actor_incoming_team
from ...database.models.common import GameStatus
from ...database.requests.actor import get_free_actors_in_game
from ...database.requests.game import get_game_by_code, start_game
from ...database.requests.stage import find_and_assign_next_actor
from ...database.requests.team import get_ready_teams
from ...keyboards.author import author_dashboard
from ...states import AuthorStates


router = Router()


@router.message(AuthorStates.dashboard, F.text == "🚀 Запустить игру")
async def do_start_game(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    game = await get_game_by_code(data['game_code'])

    if game.status not in (GameStatus.CREATED, GameStatus.PREPARED):
        await message.answer("❌ Игра уже запущена или завершена")
        return

    ready_teams = await get_ready_teams(game.id)
    ready_actors = await get_free_actors_in_game(game.id)

    if not ready_teams:
        await message.answer("❌ Нет готовых команд. Дождитесь нажатия 'Готов к игре' от командиров")
        return
    if not ready_actors:
        await message.answer("❌ Нет готовых актёров")
        return

    game = await start_game(data['game_code'])

    assignments = []
    for team in ready_teams:
        actor = await find_and_assign_next_actor(game.id, team.id)
        if actor:
            assignments.append((team, actor))

    await message.answer(
        f"🚀 <b>Игра запущена!</b>\n\n"
        f"✅ Команд: {len(ready_teams)}\n"
        f"🎭 Актёров: {len(ready_actors)}\n"
        f"📌 Назначено этапов: {len(assignments)}",
        reply_markup=author_dashboard(game.status),
    )

    for team, actor in assignments:
        await notify_team_new_actor(bot, team, actor)
        await notify_actor_incoming_team(bot, actor, team)
