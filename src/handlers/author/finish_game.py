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

from ...database.models.common import GameStatus
from ...database.requests.game import get_game_by_code, finish_game
from ...database.requests.stage import get_game_results
from ...keyboards.author import confirm_finish_game, author_main
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data.startswith("author:finish_game:"))
async def finish_game_prompt(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 2)[2]
    await safe_edit(
        callback,
        "⚠️ <b>Завершить игру?</b>\n\nВсе активные этапы будут остановлены. Действие необратимо",
        confirm_finish_game(code),
    )


@router.callback_query(F.data.startswith("author:confirm_finish:"))
async def confirm_finish(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    if game.status != GameStatus.RUNNING:
        await callback.answer("Игра не запущена", show_alert=True)
        return

    await finish_game(code)
    results = await get_game_results(game.id)

    medals = ["🥇", "🥈", "🥉"]
    text = "🏁 <b>Игра завершена!</b>\n\n📊 <b>Итоговый рейтинг:</b>\n\n"
    for i, r in enumerate(results, 1):
        medal = medals[i - 1] if i <= 3 else f"{i}"
        text += f"{medal} <b>{esc(r['team'].name)}</b> - {r['total']} баллов\n"

    await state.set_state(None)
    await safe_edit(callback, text, author_main())
