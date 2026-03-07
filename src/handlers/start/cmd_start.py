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
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ...database.models.common import GameStatus
from ...database.requests.game import get_game_by_code, get_game_by_actor_code
from ...database.requests.user import get_or_create_user
from ...keyboards.author import author_main
from ...states import JoinCommanderStates, JoinActorStates
from ...utils.escape import esc

router = Router()


_JOINABLE = (GameStatus.CREATED, GameStatus.PREPARED, GameStatus.RUNNING)


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    args = command.args
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if not args:
        await state.clear()
        await state.update_data(user_id=str(user.id))
        await message.answer(
            "👋 <b>QuestBot</b>\n\nВыберите действие:",
            reply_markup=author_main(),
        )
        return

    code = args.strip().upper()

    game = await get_game_by_code(code)
    if game:
        if game.status not in _JOINABLE:
            await message.answer("❌ Эта игра уже завершена или недоступна")
            return
        await state.clear()
        await state.update_data(
            user_id=str(user.id), game_id=str(game.id), game_code=game.code
        )
        await state.set_state(JoinCommanderStates.waiting_team_name)
        title = esc(game.title) or f"Игра {game.code}"
        await message.answer(
            f"👥 <b>Регистрация командира</b>\n"
            f"🎮 Игра: <b>{title}</b>\n\n"
            f"Введите название вашей команды:"
        )
        return

    game = await get_game_by_actor_code(code)
    if game:
        if game.status not in _JOINABLE:
            await message.answer("❌ Эта игра уже завершена или недоступна")
            return
        await state.clear()
        await state.update_data(
            user_id=str(user.id), game_id=str(game.id), game_code=game.code
        )
        await state.set_state(JoinActorStates.waiting_character_name)
        title = esc(game.title) or f"Игра {game.actor_code}"
        await message.answer(
            f"🎭 <b>Регистрация актёра</b>\n"
            f"🎮 Игра: <b>{title}</b>\n\n"
            f"Введите имя вашего персонажа:"
        )
        return

    await message.answer("❌ Игра с таким кодом не найдена")
