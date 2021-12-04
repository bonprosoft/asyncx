import asyncio

import pytest

import asyncx


@pytest.mark.asyncio
async def test_just() -> None:
    coro_int = asyncx.just(1)
    assert asyncio.iscoroutine(coro_int)
    assert await coro_int == 1

    obj = object()
    coro_obj = asyncx.just(obj)
    assert asyncio.iscoroutine(coro_obj)
    assert await coro_obj is obj
