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

from sqlalchemy import select

from uuid import UUID

from ... import database_session
from ...models import TeamModel


async def delete_team(team_id: UUID) -> bool:
    async with database_session() as session:
        team = await session.scalar(select(TeamModel).where(TeamModel.id == team_id))
        if team is None:
            return False
        await session.delete(team)
        await session.flush()
        return True
