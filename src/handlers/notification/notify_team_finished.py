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

from aiogram import Bot

from ...database.models import TeamModel
from ...database.requests.user import get_user_by_id
from ...keyboards.commander import commander_finished
from ...states import CommanderStates
from ...utils.logging import get_logger


_logger = get_logger(__name__)


async def notify_team_finished(bot: Bot, team: TeamModel) -> None:
    user = await get_user_by_id(team.commander_id)
    if not user:
        return
    try:
        await set_user_state(user.telegram_id, CommanderStates.finished.state)
        await bot.send_message(
            user.telegram_id,
            "🏁 <b>Поздравляем! Вы прошли всех актёров!</b>\n\nОжидайте итогов от организатора",
            reply_markup=commander_finished(),
        )
    except Exception as e:
        _logger.warning(
            "Не удалось уведомить командира о финише %s: %s", user.telegram_id, e
        )
