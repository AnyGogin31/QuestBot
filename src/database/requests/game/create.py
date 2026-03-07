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

from secrets import choice

from sqlalchemy import (
    func,
    or_,
    select
)

from ... import database_session
from ...models import GameModel
from ...models.common import GameStatus


_CONSONANTS = 'BCDFGHJKLMNPRSTVWXZ'
_VOWELS = 'AEIOU'
_ACTIVE = (GameStatus.CREATED, GameStatus.PREPARED, GameStatus.RUNNING)


def _phonetic():
    c, v = _CONSONANTS, _VOWELS
    return (
            choice(v) + choice(c) + choice(v) + choice(c) + choice(v) +
            choice(c) + choice(v) + choice(c) + choice(v) + choice(c)
    )


async def _is_free(session, code):
    count = await session.scalar(
        select(func.count()).select_from(GameModel).where(
            GameModel.status.in_(_ACTIVE),
            or_(GameModel.code == code, GameModel.actor_code == code)
        )
    )
    return (count or 0) == 0


async def _unique_codes(session):
    for _ in range(300):
        cmd, act = _phonetic(), _phonetic()
        if cmd != act and await _is_free(session, cmd) and await _is_free(session, act):
            return cmd, act
    raise RuntimeError('Не удалось сгенерировать уникальные коды игры')


async def create_game(
        author_id: UUID,
        title: str | None = None,
        description: str | None = None,
        min_score: int = 0,
        max_score: int = 10
) -> GameModel:
    async with database_session() as session:
        cmd_code, act_code = await _unique_codes(session)
        game = GameModel(
            code=cmd_code,
            actor_code=act_code,
            author_id=author_id,
            title=title,
            description=description,
            min_score=min_score,
            max_score=max_score
        )
        session.add(game)
        await session.flush()
        return game
