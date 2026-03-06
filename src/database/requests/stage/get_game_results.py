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

from sqlalchemy import select

from ... import database_session
from ...models import ActorModel, TeamModel, StageModel
from ...models.common import StageStatus


async def get_game_results(
        game_id: UUID
):
    async with database_session() as session:
        teams_result = await session.execute(
            select(TeamModel).where(TeamModel.game_id == game_id)
        )
        teams = teams_result.scalars().all()

        results = []
        for team in teams:
            rows = await session.execute(
                select(StageModel, ActorModel)
                    .join(ActorModel, StageModel.actor_id == ActorModel.id)
                    .where(
                        StageModel.team_id == team.id,
                        StageModel.status == StageStatus.COMPLETED
                    )
            )
            stages = rows.all()
            total = sum((row.StageModel.score or 0) for row in stages)
            results.append({'team': team, 'stages': stages, 'total': total})
        results.sort(key=lambda r: r['total'], reverse=True)
        return results
