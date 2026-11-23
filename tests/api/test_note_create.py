import pytest

from httpx import AsyncClient
from tests.conftest import auth_headers

pytest = pytest.mark.asyncio


@pytest
async def test_create_note_success(
        client: AsyncClient,
        auth_headers
):
    body = {
        "title": "Title",
        "content": "Some content",
        "is_archived": False,
        "tags": [
            "python"
        ]
    }
    response = await client.post(
        '/notes/',
        json=body,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()['title'] == body['title']
    assert response.json()['is_archived'] == body['is_archived']
    assert response.json()['tags'] == body['tags']


@pytest
async def test_create_note_without_token(client: AsyncClient):
    response = await client.post(
        "/notes/",
        json={
            "title": "Title",
            "content": "Some content",
            "is_archived": False,
            "tags": [
                "python"
            ]
        }
    )

    assert response.status_code == 401


@pytest
async def test_create_note_with_invalid_token(client: AsyncClient):
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
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


@pytest
async def test_create_note_with_malformed_auth_header(client: AsyncClient):
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
        headers={
            "Authorization": "invalid"
        }
    )

    assert response.status_code == 401

@pytest
async def test_create_note_missing_title(client: AsyncClient, auth_headers):
    response = await client.post(
        "/notes/",
        json={
            "content": "Some content",
            "is_archived": False,
            "tags": [
                "python"
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest
async def test_create_note_with_missing_content(client: AsyncClient, auth_headers):
    response = await client.post(
        "/notes/",
        json={
            "title": "Title",
            "is_archived": False,
            "tags": [
                "python"
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 422

@pytest
async def test_create_note_invalid_title_type(
        client: AsyncClient,
        auth_headers
):
    response = await client.post(
        "/notes/",
        json={
            "title": 123456,
            "content": "Some content",
            "is_archived": False,
            "tags": [
                "python"
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 422
