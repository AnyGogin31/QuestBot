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

from ...database.models.common import GameStatus
from ...database.requests.game import get_game_by_code, finish_game
from ...database.requests.stage import get_game_results
from ...keyboards.author import confirm_finish_game, author_main
from ...states import AuthorStates


router = Router()


@router.message(AuthorStates.dashboard, F.text == "🏁 Завершить игру")
async def finish_game_prompt(message: Message) -> None:
    await message.answer(
        "⚠️ <b>Завершить игру?</b>\n\nВсе активные этапы будут остановлены. Действие необратимо",
        reply_markup=confirm_finish_game(),
    )


@router.callback_query(F.data == "confirm_finish_game")
async def confirm_finish(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    game = await get_game_by_code(data["game_code"])
    if game.status != GameStatus.RUNNING:
        await callback.answer("Игра не запущена")
        return

    await finish_game(data["game_code"])
    results = await get_game_results(game.id)

    await callback.message.delete()
    medals = ["🥇", "🥈", "🥉"]
    text = "🏁 <b>Игра завершена!</b>\n\n📊 <b>Итоги:</b>\n\n"
    for i, r in enumerate(results, 1):
        medal = medals[i - 1] if i <= 3 else f"{i}."
        text += f"{medal} <b>{r['team'].name}</b> — {r['total']} баллов\n"

    await callback.message.answer(text, reply_markup=author_main())
    await state.set_state(AuthorStates.main)


@router.callback_query(F.data == "cancel_finish_game")
async def cancel_finish(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer("Отменено")
