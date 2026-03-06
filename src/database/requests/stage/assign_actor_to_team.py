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

from ... import database_session
from ...models import ActorModel, StageModel
from ...models.common import ActorStatus


async def assign_actor_to_team(
        game_id: UUID,
        team_id: UUID,
        actor: ActorModel
):
    stage = StageModel(
        game_id=game_id,
        team_id=team_id,
        actor_id=actor.id
    )

    async with database_session() as session:
        actor.status = ActorStatus.BUSY
        session.add(stage)
        await session.flush()
        return stage
