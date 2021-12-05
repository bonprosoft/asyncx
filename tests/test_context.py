import asyncio
import contextlib
from typing import List

import pytest

import asyncx


@pytest.mark.asyncio
async def test_acontext() -> None:
    ret: List[int] = []

    async def fake(val: int) -> int:
        await asyncio.sleep(val * 0.01)
        ret.append(val)
        return val

    async with asyncx.acontext(fake(1)) as t:
        await asyncio.sleep(0.1)
        assert t.done()

    assert await t == 1
    assert ret == [1]

    async with asyncx.acontext(fake(2)) as t:
        assert not t.done()

    await asyncio.sleep(0.1)
    assert t.cancelled()
    assert ret == [1]


@pytest.mark.asyncio
async def test_acontext_overload() -> None:
    ret: List[int] = []
    loop = asyncio.get_running_loop()

    async def fake(val: int) -> int:
        await asyncio.sleep(1.0)
        ret.append(val)
        return val

    coro_context: asyncio.Task[int]
    task_context: asyncio.Task[int]
    future_context: asyncio.Future[int]

    async with contextlib.AsyncExitStack() as stack:
        coro = fake(1)
        coro_context = await stack.enter_async_context(asyncx.acontext(coro))

        task = asyncio.create_task(fake(1))
        task_context = await stack.enter_async_context(asyncx.acontext(task))

        future: asyncio.Future[int] = loop.create_future()
        future_context = await stack.enter_async_context(asyncx.acontext(future))

    await asyncio.sleep(0.1)
    assert coro_context.cancelled()
    assert task_context.cancelled()
    assert future_context.cancelled()
    assert ret == []
