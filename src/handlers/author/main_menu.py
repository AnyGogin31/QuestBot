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

from uuid import UUID

from ...database.requests.game import get_games_by_author, get_game_by_code
from ...keyboards.author import games_list, author_main, author_dashboard
from ...states import AuthorStates, CreateGameStates

router = Router()


@router.message(AuthorStates.main, F.text == "🎮 Создать новую игру")
async def to_create_game(message: Message, state: FSMContext):
    await state.set_state(CreateGameStates.waiting_title)
    await message.answer(
        "🎮 <b>Создание игры</b>\n\nВведите название игры (или /skip):"
    )


@router.message(AuthorStates.main, F.text == "📋 Мои игры")
async def my_games(message: Message, state: FSMContext):
    data = await state.get_data()
    games = await get_games_by_author(UUID(data["user_id"]))
    if not games:
        await message.answer("У вас пока нет игр")
        return
    await message.answer("📋 <b>Ваши игры:</b>", reply_markup=games_list(games))


@router.message(AuthorStates.dashboard, F.text == "🔙 Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.set_state(AuthorStates.main)
    await message.answer("Главное меню:", reply_markup=author_main())


@router.callback_query(F.data.startswith("open_game:"))
async def open_game(callback: CallbackQuery, state: FSMContext):
    code = callback.data.split(":", 1)[1]
    game = await get_game_by_code(code)
    if not game:
        await callback.answer("Игра не найдена")
        return
    await state.set_state(AuthorStates.dashboard)
    await state.update_data(game_code=game.code)
    await callback.message.delete()
    title = game.title or f"Игра {game.code}"
    await callback.message.answer(
        f"📊 <b>Дашборд: {title}</b>\n"
        f"🔑 Командирский код: <code>{game.code}</code>\n"
        f"🎭 Актёрский код: <code>{game.actor_code}</code>",
        reply_markup=author_dashboard(game.status),
    )
