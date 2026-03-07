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

from sqlalchemy import select, func

from ... import database_session
from ...models import ActorModel, StageModel, TeamModel
from ...models.common import ActorStatus, StageStatus, TeamStatus


async def get_game_stats(game_id: UUID):
    async with database_session() as session:
        total_teams = (
            await session.scalar(
                select(func.count())
                .select_from(TeamModel)
                .where(TeamModel.game_id == game_id)
            )
            or 0
        )
        finished_teams = (
            await session.scalar(
                select(func.count())
                .select_from(TeamModel)
                .where(
                    TeamModel.game_id == game_id,
                    TeamModel.status == TeamStatus.FINISHED,
                )
            )
            or 0
        )
        free_actors = (
            await session.scalar(
                select(func.count())
                .select_from(ActorModel)
                .where(
                    ActorModel.game_id == game_id, ActorModel.status == ActorStatus.FREE
                )
            )
            or 0
        )
        busy_actors = (
            await session.scalar(
                select(func.count())
                .select_from(ActorModel)
                .where(
                    ActorModel.game_id == game_id, ActorModel.status == ActorStatus.BUSY
                )
            )
            or 0
        )
        total_stages = (
            await session.scalar(
                select(func.count())
                .select_from(StageModel)
                .where(StageModel.game_id == game_id)
            )
            or 0
        )
        done_stages = (
            await session.scalar(
                select(func.count())
                .select_from(StageModel)
                .where(
                    StageModel.game_id == game_id,
                    StageModel.status == StageStatus.COMPLETED,
                )
            )
            or 0
        )
    return {
        "total_teams": total_teams,
        "finished_teams": finished_teams,
        "active_teams": total_teams - finished_teams,
        "free_actors": free_actors,
        "busy_actors": busy_actors,
        "total_stages": total_stages,
        "done_stages": done_stages,
    }
