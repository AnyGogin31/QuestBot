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
from ...models import ActorModel


_UNSET = object()


async def update_actor(
    actor_id: UUID,
    name: object = _UNSET,
    location: object = _UNSET,
    description: object = _UNSET,
    min_score: object = _UNSET,
    max_score: object = _UNSET,
):
    async with database_session() as session:
        actor = await session.scalar(
            select(ActorModel).where(ActorModel.id == actor_id)
        )
        if actor is None:
            return None
        if name is not _UNSET:
            actor.name = name
        if location is not _UNSET:
            actor.location = location
        if description is not _UNSET:
            actor.description = description
        if min_score is not _UNSET:
            actor.min_score = min_score
        if max_score is not _UNSET:
            actor.max_score = max_score
        await session.flush()
        return actor
