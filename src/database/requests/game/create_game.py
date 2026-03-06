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

import random

import string

from uuid import UUID

from sqlalchemy import select

from ... import database_session
from ...models import GameModel


def _generate_code(length: int = 7) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def create_game(
        author_id: UUID,
        title: str | None = None,
        description: str | None = None,
        min_score: int = 0,
        max_score: int = 10
):
    async with database_session() as session:
        while True:
            code = _generate_code()
            existing = await session.scalar(select(GameModel).where(GameModel.code == code))
            if existing is None:
                break
        game = GameModel(
            code=code,
            author_id=author_id,
            title=title,
            description=description,
            min_score=min_score,
            max_score=max_score,
        )
        session.add(game)
        await session.flush()
        return game
