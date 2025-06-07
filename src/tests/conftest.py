import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from config import get_settings
from database import reset_database, get_db_contextmanager
from database.populate import CSVDatabaseSeeder
from main import app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db():
    """
    Reset the SQLite database before each test.

    This fixture ensures that the database is cleared and recreated for every test function.
    It helps maintain test isolation by preventing data leakage between tests.
    """
    await reset_database()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provide an asynchronous test client for making HTTP requests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Provide an async database session for database interactions.

    This fixture yields an async session using `get_db_contextmanager`, ensuring that the session
    is properly closed after each test.
    """
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def seed_database(db_session):
    """
    Seed the database with test data if it is empty.

    This fixture initializes a `CSVDatabaseSeeder` and ensures the test database is populated before
    running tests that require existing data.

    :param db_session: The async database session fixture.
    :type db_session: AsyncSession
    """
    settings = get_settings()
    seeder = CSVDatabaseSeeder(
        csv_file_path=settings.PATH_TO_MOVIES_CSV, db_session=db_session
    )

    if not await seeder.is_db_populated():
        await seeder.seed()

    yield db_session
