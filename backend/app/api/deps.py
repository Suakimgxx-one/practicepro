from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# Re-exported so route modules import everything from app.api.deps
# rather than reaching into app.db directly — keeps the DI surface
# in one place as the app grows (e.g. auth deps will live here too).
DBSession = Annotated[AsyncSession, Depends(get_db)]


class Pagination:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        self.limit = limit
        self.offset = offset


PaginationParams = Annotated[Pagination, Depends()]
