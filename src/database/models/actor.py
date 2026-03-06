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

from typing import Optional

from uuid import (
    UUID,
    uuid7
)

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    func,
    String,
    Text,
    Uuid
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import BaseModel
from .common import ActorStatus


class ActorModel(BaseModel):
    __tablename__ = 'actors'

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7
    )

    game_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("games.id")
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id")
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255)
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text
    )

    status: Mapped[ActorStatus] = mapped_column(
        Enum(ActorStatus),
        default=ActorStatus.FREE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
