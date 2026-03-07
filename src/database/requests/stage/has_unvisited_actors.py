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

from ... import database_session
from ...models import ActorModel, StageModel


async def has_unvisited_actors(game_id: UUID, team_id: UUID):
    async with database_session() as session:
        visited_sq = select(StageModel.actor_id).where(StageModel.team_id == team_id)
        count = await session.scalar(
            select(func.count())
            .select_from(ActorModel)
            .where(ActorModel.game_id == game_id, ActorModel.id.not_in(visited_sq))
        )
        return (count or 0) > 0
