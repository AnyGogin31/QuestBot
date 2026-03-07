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
from ...models import ActorModel, TeamModel, StageModel
from ...models.common import ActorStatus, TeamStatus, StageStatus


async def find_and_assign_waiting_team(game_id: UUID, actor_id: UUID):
    async with database_session() as session:
        teams = list(
            (
                await session.execute(
                    select(TeamModel).where(
                        TeamModel.game_id == game_id,
                        TeamModel.status != TeamStatus.FINISHED,
                    )
                )
            )
            .scalars()
            .all()
        )

        for team in teams:
            active = await session.scalar(
                select(StageModel).where(
                    StageModel.team_id == team.id,
                    StageModel.status.in_(
                        [StageStatus.ASSIGNED, StageStatus.IN_PROGRESS]
                    ),
                )
            )
            if active is not None:
                continue

            already = await session.scalar(
                select(func.count())
                .select_from(StageModel)
                .where(StageModel.team_id == team.id, StageModel.actor_id == actor_id)
            )
            if (already or 0) > 0:
                continue

            visited_sq = select(StageModel.actor_id).where(
                StageModel.team_id == team.id
            )
            remaining = await session.scalar(
                select(func.count())
                .select_from(ActorModel)
                .where(ActorModel.game_id == game_id, ActorModel.id.not_in(visited_sq))
            )
            if (remaining or 0) == 0:
                continue

            actor = await session.scalar(
                select(ActorModel).where(ActorModel.id == actor_id)
            )
            stage = StageModel(game_id=game_id, team_id=team.id, actor_id=actor_id)
            actor.status = ActorStatus.BUSY
            session.add(stage)
            await session.flush()
            return team

        return None
