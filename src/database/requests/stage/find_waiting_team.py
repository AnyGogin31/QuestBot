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

from sqlalchemy import func, select

from .get_active_stage_for_team import get_active_stage_for_team
from .has_unvisited_actors import has_unvisited_actors
from ... import database_session
from ...models import StageModel, TeamModel
from ...models.common import TeamStatus


async def find_waiting_team(
        game_id: UUID,
        actor_id: UUID
):
    async with database_session() as session:
        result = await session.execute(
            select(TeamModel).where(
                TeamModel.game_id == game_id,
                TeamModel.status != TeamStatus.FINISHED
            )
        )
        teams = result.scalars().all()
        for team in teams:
            active = await get_active_stage_for_team(team.id)
            if active is not None:
                continue
            visited_count = await session.scalar(
                select(func.count()).select_from(StageModel).where(
                    StageModel.team_id == team.id,
                    StageModel.actor_id == actor_id
                )
            )
            if (visited_count or 0) > 0:
                continue
            if await has_unvisited_actors(game_id, team.id):
                return team
        return None
