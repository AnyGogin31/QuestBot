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

from aiogram.utils.keyboard import InlineKeyboardBuilder


def actor_fields(actor_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Имя персонажа", callback_data=f"actor_field:{actor_id}:name"
    )
    builder.button(text="📍 Локация", callback_data=f"actor_field:{actor_id}:location")
    builder.button(
        text="📋 Описание", callback_data=f"actor_field:{actor_id}:description"
    )
    builder.button(
        text="⬇️ Мин. балл", callback_data=f"actor_field:{actor_id}:min_score"
    )
    builder.button(
        text="⬆️ Макс. балл", callback_data=f"actor_field:{actor_id}:max_score"
    )
    builder.button(text="❌ Отмена", callback_data="edit_cancel")
    builder.adjust(2)
    return builder.as_markup()
