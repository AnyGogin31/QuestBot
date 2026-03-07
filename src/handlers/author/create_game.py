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

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from uuid import UUID

from ...database.requests.game import create_game
from ...keyboards.author import author_dashboard
from ...states import CreateGameStates, AuthorStates


router = Router()


@router.message(CreateGameStates.waiting_title)
async def step_title(message: Message, state: FSMContext) -> None:
    title = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(title=title)
    await state.set_state(CreateGameStates.waiting_description)
    await message.answer("Введите описание игры (или /skip):")


@router.message(CreateGameStates.waiting_description)
async def step_description(message: Message, state: FSMContext) -> None:
    desc = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(CreateGameStates.waiting_min_score)
    await message.answer("Введите минимальный балл (целое число, например <b>0</b>):")


@router.message(CreateGameStates.waiting_min_score)
async def step_min_score(message: Message, state: FSMContext) -> None:
    try:
        min_score = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите целое число")
        return
    await state.update_data(min_score=min_score)
    await state.set_state(CreateGameStates.waiting_max_score)
    await message.answer("Введите максимальный балл (целое число, например <b>10</b>):")


@router.message(CreateGameStates.waiting_max_score)
async def step_max_score(message: Message, state: FSMContext) -> None:
    try:
        max_score = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите целое число")
        return
    data = await state.get_data()
    min_score = data.get("min_score", 0)
    if max_score <= min_score:
        await message.answer(f"❌ Максимум должен быть больше минимума ({min_score})")
        return

    game = await create_game(
        author_id=UUID(data["user_id"]),
        title=data.get("title"),
        description=data.get("description"),
        min_score=min_score,
        max_score=max_score,
    )

    await state.set_state(AuthorStates.dashboard)
    await state.update_data(game_code=game.code)
    await message.answer(
        f"✅ <b>Игра создана!</b>\n\n"
        f"📛 <b>Название:</b> {game.title or 'Без названия'}\n"
        f"⚖️ <b>Баллы:</b> {min_score} – {max_score}\n\n"
        f"🔑 <b>Ссылка для командиров:</b>\n<code>/start {game.code}</code>\n\n"
        f"🎭 <b>Ссылка для актёров:</b>\n<code>/start {game.actor_code}</code>",
        reply_markup=author_dashboard(game.status),
    )
