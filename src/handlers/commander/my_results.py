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

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from uuid import UUID

from ...database.requests.stage import get_team_completed_stages
from ...keyboards.commander import commander_finished
from ...states import CommanderStates
from ...utils.escape import esc
from ...utils.safe_edit import safe_edit

router = Router()


@router.callback_query(F.data == "commander:results", CommanderStates.finished)
async def my_results(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    stages = await get_team_completed_stages(UUID(data["team_id"]))

    if not stages:
        await callback.answer("Результатов пока нет", show_alert=True)
        return

    text = "🏆 <b>Ваши результаты:</b>\n\n"
    total = 0
    for row in stages:
        s, a = row.StageModel, row.ActorModel
        text += f"🎭 {esc(a.name)}: <b>{s.score}</b> баллов\n"
        total += s.score or 0
    text += f"\n<b>Итого: {total} баллов</b>"
    await safe_edit(callback, text, commander_finished())
