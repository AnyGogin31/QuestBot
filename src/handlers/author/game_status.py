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

from ...database.requests.game import get_game_by_code
from ...database.requests.stage import get_game_stats
from ...keyboards.author import author_dashboard

router = Router()


@router.callback_query(F.data.startswith("author:game_status:"))
async def game_status(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    s = await get_game_stats(game.id)
    pct = round(s["done_stages"] / s["total_stages"] * 100) if s["total_stages"] else 0

    await callback.message.edit_text(
        f"📊 <b>Статус игры {game.code}</b>\n\n"
        f"👥 Активных команд: {s['active_teams']}\n"
        f"🏁 Финишировавших: {s['finished_teams']}\n"
        f"🎭 Свободных актёров: {s['free_actors']}\n"
        f"🔄 Занятых актёров: {s['busy_actors']}\n"
        f"📈 Этапов: {s['done_stages']}/{s['total_stages']} ({pct}%)",
        reply_markup=author_dashboard(code, game.status),
    )
