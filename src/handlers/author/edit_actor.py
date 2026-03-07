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
from uuid import UUID

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from ...database.requests.actor import get_actors_in_game, update_actor, get_actor_by_id
from ...database.requests.game import get_game_by_code
from ...keyboards.author import author_dashboard
from ...keyboards.author.actor_fields import actor_fields
from ...states import AuthorStates
from ...states.author import EditActorStates

router = Router()


_FIELD_LABELS = {
    'name': 'имя персонажа',
    'location': 'локацию',
    'description': 'описание',
    'min_score': 'минимальный балл',
    'max_score': 'максимальный балл',
}


@router.message(AuthorStates.dashboard, F.text == "✏️ Изменить актёра")
async def edit_actor_start(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game = await get_game_by_code(data['game_code'])
    actors = await get_actors_in_game(game.id)
    if not actors:
        await message.answer("Нет зарегистрированных актёров")
        return
    await state.set_state(EditActorStates.select_actor)
    await message.answer("Выберите актёра для редактирования:", reply_markup=actors_edit_kb(actors))


@router.callback_query(F.data.startswith("edit_actor:"), EditActorStates.select_actor)
async def edit_actor_select(callback: CallbackQuery, state: FSMContext) -> None:
    actor_id = callback.data.split(":", 1)[1]
    await state.update_data(edit_actor_id=actor_id)
    await state.set_state(EditActorStates.select_field)
    await callback.message.edit_reply_markup(reply_markup=actor_fields(actor_id))


@router.callback_query(F.data.startswith("actor_field:"), EditActorStates.select_field)
async def edit_actor_field_select(callback: CallbackQuery, state: FSMContext) -> None:
    _, actor_id, field = callback.data.split(":")
    await state.update_data(edit_actor_field=field)
    await callback.message.delete()
    label = _FIELD_LABELS.get(field, field)
    state_map = {
        'name': EditActorStates.waiting_name,
        'location': EditActorStates.waiting_location,
        'description': EditActorStates.waiting_description,
        'min_score': EditActorStates.waiting_min_score,
        'max_score': EditActorStates.waiting_max_score,
    }
    await state.set_state(state_map[field])
    if field in ('location', 'description'):
        await callback.message.answer(f"Введите {label} (или /skip для очистки):")
    else:
        await callback.message.answer(f"Введите {label}:")


async def _finish_edit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game = await get_game_by_code(data['game_code'])
    await state.set_state(AuthorStates.dashboard)
    await message.answer("✅ Данные актёра обновлены", reply_markup=author_dashboard(game.status))


@router.message(EditActorStates.waiting_name)
async def edit_actor_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name:
        await message.answer("❌ Имя не может быть пустым")
        return
    data = await state.get_data()
    await update_actor(UUID(data['edit_actor_id']), name=name)
    await _finish_edit(message, state)


@router.message(EditActorStates.waiting_location)
async def edit_actor_location(message: Message, state: FSMContext) -> None:
    loc = None if message.text.strip() == '/skip' else message.text.strip()
    data = await state.get_data()
    await update_actor(UUID(data['edit_actor_id']), location=loc)
    await _finish_edit(message, state)


@router.message(EditActorStates.waiting_description)
async def edit_actor_description(message: Message, state: FSMContext) -> None:
    desc = None if message.text.strip() == '/skip' else message.text.strip()
    data = await state.get_data()
    await update_actor(UUID(data['edit_actor_id']), description=desc)
    await _finish_edit(message, state)


@router.message(EditActorStates.waiting_min_score)
async def edit_actor_min_score(message: Message, state: FSMContext) -> None:
    try:
        val = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите целое число")
        return
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data['edit_actor_id']))
    game = await get_game_by_code(data['game_code'])
    max_s = actor.max_score if actor.max_score is not None else game.max_score
    if val >= max_s:
        await message.answer(f"❌ Минимум должен быть меньше максимума ({max_s})")
        return
    await update_actor(actor.id, min_score=val)
    await _finish_edit(message, state)


@router.message(EditActorStates.waiting_max_score)
async def edit_actor_max_score(message: Message, state: FSMContext) -> None:
    try:
        val = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите целое число")
        return
    data = await state.get_data()
    actor = await get_actor_by_id(UUID(data['edit_actor_id']))
    game = await get_game_by_code(data['game_code'])
    min_s = actor.min_score if actor.min_score is not None else game.min_score
    if val <= min_s:
        await message.answer(f"❌ Максимум должен быть больше минимума ({min_s})")
        return
    await update_actor(actor.id, max_score=val)
    await _finish_edit(message, state)
