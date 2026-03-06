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

from datetime import datetime

from typing import (
    List,
    Optional
)

from uuid import (
    UUID,
    uuid7
)

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    func,
    Integer,
    JSON,
    String,
    Text,
    Uuid
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import BaseModel
from .common import GameStatus


class GameModel(BaseModel):
    __tablename__ = 'games'

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7
    )

    code: Mapped[str] = mapped_column(
        String(10),
        unique=True
    )

    author_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id")
    )

    admin_ids: Mapped[List[UUID]] = mapped_column(
        JSON,
        default=list
    )

    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus),
        default=GameStatus.CREATED
    )

    min_score: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    max_score: Mapped[int] = mapped_column(
        Integer,
        default=10
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255)
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )

    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )
