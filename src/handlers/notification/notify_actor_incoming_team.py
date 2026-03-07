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

from ...database.models import ActorModel, TeamModel
from ...database.requests.user import get_user_by_id
from ...keyboards.actor import actor_in_game
from ...utils.logging import get_logger


_logger = get_logger(__name__)


async def notify_actor_incoming_team(bot: Bot, actor: ActorModel, team: TeamModel) -> None:
    user = await get_user_by_id(actor.user_id)
    if not user:
        return
    text = (
        f"👥 <b>К вам направляется команда!</b>\n\n"
        f"🏷 <b>Название:</b> {team.name}\n"
        f"👤 <b>Участников:</b> {team.member_count}\n"
    )
    try:
        await bot.send_message(user.telegram_id, text, reply_markup=actor_in_game())
    except Exception as e:
        _logger.warning("Не удалось уведомить актёра %s: %s", user.telegram_id, e)
