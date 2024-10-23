import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = None

    def init_session_maker(self):
        """ Инициализировать sessionmaker отдельно, после создания движка. """
        if not self._session_maker:
            self._session_maker = async_sessionmaker(
                autoflush=False,
                autocommit=False,
                bind=self._engine
            )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session maker is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(f"Session error: {err}")
            await session.rollback()
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(config.DB_URL)
sessionmanager.init_session_maker()  # Не забудьте инициализировать сессии

async def get_db():
    async with sessionmanager.session() as session:
        try:
            yield session
        except Exception as e:
            print(f'Database error: {e}')
            raise  # Повторно выбросить исключение для его обработки FastAPI