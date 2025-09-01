import asyncio

import pytest
from service.session.core.management import InitRedis


@pytest.mark.asyncio
async def test_redis_connection():
    r = InitRedis()

    assert await r.ping()


@pytest.mark.asyncio
async def test_set_session():
    r = InitRedis()
    await r.set_session("test_session", {"user_id": "123"})
    assert await r.get_session("test_session")


@pytest.mark.asyncio
async def test_get_session():
    r = InitRedis()
    await r.set_session("test_session", {"user_id": "123"})
    assert await r.get_session("test_session") == {"user_id": "123"}


@pytest.mark.asyncio
async def test_get_none_session():
    r = InitRedis()
    await r.set_session("test_session", {"user_id": "123"})
    assert await r.get_session("test_") == "Does Not Exist!"


@pytest.mark.asyncio
async def test_delete_session():
    r = InitRedis()
    await r.set_session("test_session", {"user_id": "123"})
    await r.delete_session("test_session")
    assert await r.get_session("test_session") == "Does Not Exist!"
