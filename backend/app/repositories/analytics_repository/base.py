from sqlalchemy.ext.asyncio import AsyncSession


class BaseAnalyticsRepository:
    """
    Base repository shared by all analytics repository mixins.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db