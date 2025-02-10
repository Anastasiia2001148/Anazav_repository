import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import config


class DataBaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")

        session = self._session_maker()

        try:
            yield session
        except Exception as error:
            print(error)
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(config.DB_URL)


# Dependency
async def get_db():
    async with sessionmanager.session() as session:
        yield session
