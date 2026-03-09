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
from ...database.requests.game import get_game_by_code, cancel_game
from ...keyboards.author import author_main
from ...keyboards.author.confirm_cancel import confirm_cancel as confirm_cancel_kb
from ...utils.safe_edit import safe_edit

router = Router()


_CANCELLABLE = (GameStatus.CREATED, GameStatus.PREPARED, GameStatus.RUNNING)


@router.callback_query(F.data.startswith("author:cancel_game:"))
async def cancel_game_prompt(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 2)[2]
    await safe_edit(
        callback,
        "⚠️ <b>Отменить игру?</b>\n\n"
        "Все участники потеряют доступ к игре. Действие необратимо",
        confirm_cancel_kb(code),
    )


@router.callback_query(F.data.startswith("author:confirm_cancel:"))
async def confirm_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    if game is None or game.status not in _CANCELLABLE:
        await callback.answer(
            "Невозможно отменить игру в текущем статусе", show_alert=True
        )
        return
    await cancel_game(code)
    await state.set_state(None)
    await safe_edit(
        callback,
        "❌ <b>Игра отменена</b>",
        author_main(),
    )
