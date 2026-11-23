import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
connect_args = {"check_same_thread": False}
TestSession = async_sessionmaker(bind=test_engine)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as session:
        await session.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(client: AsyncClient, id: int):
    user_data = {
        'username': f'test_user_{id}',
        'email': f'user{id}@test.com',
        'password': 'test@123'
    }
    register = await client.post('/auth/register', json=user_data)
    user_data.pop('email')

    data = {
        'grant_type': "password",
        'scope': "",
        'client_id': "",
        'client_secret': ""
    }
    data = user_data | data
    token =  await client.post('/auth/login', data=data)
    assert token.status_code == 200
    return token



@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, user_id: int = 1):
    token = await create_test_user(client, user_id)
    return {"Authorization": f"Bearer {token.json()['access_token']}" }


@pytest_asyncio.fixture
async def test_note(
        client: AsyncClient,
        auth_headers
):
    response = await client.post(
        "/notes/",
        json={
            "title": "Title",
            "content": "Some content",
            "is_archived": False,
            "tags": [
                "python"
            ]
        },
        headers=auth_headers
    )

    return response.json()


