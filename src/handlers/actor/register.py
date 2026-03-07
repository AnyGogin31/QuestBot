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

from ...database.requests.actor import get_actor_by_user_and_game, create_actor
from ...database.requests.game import get_game_by_code
from ...keyboards.actor import actor_lobby
from ...states import JoinActorStates, ActorStates
from ...utils.escape import esc

router = Router()


@router.message(JoinActorStates.waiting_character_name)
async def step_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name:
        await message.answer("❌ Имя не может быть пустым")
        return
    await state.update_data(character_name=name)
    await state.set_state(JoinActorStates.waiting_location)
    await message.answer("📍 Укажите вашу локацию (или /skip):")


@router.message(JoinActorStates.waiting_location)
async def step_location(message: Message, state: FSMContext) -> None:
    loc = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(location=loc)
    await state.set_state(JoinActorStates.waiting_description)
    await message.answer("📝 Добавьте описание персонажа для команд (или /skip):")


@router.message(JoinActorStates.waiting_description)
async def step_description(message: Message, state: FSMContext) -> None:
    desc = None if message.text.strip() == "/skip" else message.text.strip()
    data = await state.get_data()
    user_id = UUID(data["user_id"])
    game_id = UUID(data["game_id"])

    game = await get_game_by_code(data["game_code"])
    existing = await get_actor_by_user_and_game(user_id, game_id)

    if existing:
        await state.set_state(ActorStates.lobby)
        await state.update_data(actor_id=str(existing.id))
        await message.answer(
            "ℹ️ Вы уже зарегистрированы как актёр", reply_markup=actor_lobby()
        )
        return

    actor = await create_actor(
        game_id=game_id,
        user_id=user_id,
        name=data["character_name"],
        location=data.get("location"),
        description=desc,
    )
    await state.set_state(ActorStates.lobby)
    await state.update_data(actor_id=str(actor.id))
    await message.answer(
        f"✅ <b>Актёр зарегистрирован!</b>\n\n"
        f"👤 <b>Персонаж:</b> {esc(data['character_name'])}\n"
        f"📍 <b>Локация:</b> {esc(data.get('location')) or 'не указана'}\n"
        f"🎮 <b>Игра:</b> {esc(game.title) or game.code}\n\n"
        f"Нажмите <b>'Готов к игре'</b>, когда займёте позицию",
        reply_markup=actor_lobby(),
    )
