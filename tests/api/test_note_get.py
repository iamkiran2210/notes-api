import uuid

import pytest
from httpx import AsyncClient
from tests.conftest import auth_headers, create_test_user, test_note

pytest = pytest.mark.asyncio


@pytest
async def test_owner_can_get_note(
        client: AsyncClient,
        auth_headers,
        test_note
):
    response = await client.get(
        f"/notes/{test_note['id']}",
        headers=auth_headers
    )

    assert response.status_code == 200

    assert response.json()['id'] == test_note['id']


@pytest
async def test_get_nonexistent_note(
        client: AsyncClient,
        auth_headers,
):
    response = await client.get(
        f"/notes/{uuid.uuid4()}",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest
async def test_user_cannot_access_other_users_note(
        client: AsyncClient,
        test_note
):
    token = await create_test_user(client, id=2)
    header = {'Authorization' : f'Bearer {token.json()['access_token']}'}

    response = await client.get(
        f"/notes/{test_note['id']}",
        headers=header
    )

    assert response.status_code in {403, 404}



