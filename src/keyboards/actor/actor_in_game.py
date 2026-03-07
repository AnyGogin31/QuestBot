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

from aiogram.utils.keyboard import ReplyKeyboardBuilder


def actor_in_game():
    button = ReplyKeyboardBuilder()
    button.button(text="🏁 Команда прибыла")
    button.button(text="✅ Этап завершён")
    button.button(text="➡️ Готов к следующей команде")
    button.button(text="📋 Список команд")
    button.adjust(2)
    return button.as_markup(resize_keyboard=True)
