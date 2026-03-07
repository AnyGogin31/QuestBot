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

from ...database.requests.game import get_games_by_author, get_game_by_code
from ...database.requests.user import get_user_by_telegram_id
from ...keyboards.author import games_list, author_main, author_dashboard
from ...states import CreateGameStates
from ...utils.escape import esc

router = Router()


@router.callback_query(F.data == "author:create_game")
async def to_create_game(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateGameStates.waiting_title)
    await callback.message.edit_text(
        "🎮 <b>Создание игры</b>\n\nВведите название игры (или /skip):"
    )


@router.callback_query(F.data == "author:my_games")
async def my_games(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    data = await state.get_data()
    user_id_raw = data.get("user_id")
    if not user_id_raw:
        user = await get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Ошибка: пользователь не найден")
            return
        user_id_raw = str(user.id)
        await state.update_data(user_id=user_id_raw)

    games = await get_games_by_author(UUID(user_id_raw))
    if not games:
        await callback.message.edit_text(
            "У вас пока нет игр",
            reply_markup=author_main(),
        )
        return
    await callback.message.edit_text(
        "📋 <b>Ваши игры:</b>", reply_markup=games_list(games)
    )


@router.callback_query(F.data == "author:back_main")
async def back_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from ...database.requests.user import get_user_by_telegram_id

    user = await get_user_by_telegram_id(callback.from_user.id)
    if user:
        await state.update_data(user_id=str(user.id))
    await callback.message.edit_text(
        "👋 <b>QuestBot</b>\n\nВыберите действие:",
        reply_markup=author_main(),
    )


@router.callback_query(F.data.startswith("author:open:"))
async def open_game(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    game = await get_game_by_code(code)
    if not game:
        await callback.answer("Игра не найдена")
        return
    await state.update_data(game_code=game.code)
    title = esc(game.title) or f"Игра {game.code}"
    await callback.message.edit_text(
        f"📊 <b>Дашборд: {title}</b>\n"
        f"🔑 Командирский код: <code>{game.code}</code>\n"
        f"🎭 Актёрский код: <code>{game.actor_code}</code>",
        reply_markup=author_dashboard(game.code, game.status),
    )
