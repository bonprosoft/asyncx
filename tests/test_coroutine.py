import asyncio
from typing import Awaitable, List

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


@pytest.mark.asyncio
async def test_wait_any_empty() -> None:
    with pytest.raises(ValueError):
        await asyncx.wait_any()


@pytest.mark.asyncio
async def test_wait_any_task() -> None:
    tasks: List[asyncio.Task[None]] = [
        asyncio.create_task(asyncio.sleep(s * 0.01)) for s in range(1, 3)
    ]
    done = await asyncx.wait_any(*tasks)
    assert done is tasks[0]
    assert all(not t.done() for t in tasks[1:])

    for t in tasks:
        t.cancel()


@pytest.mark.asyncio
async def test_wait_any_coro() -> None:
    ret: List[int] = []

    async def fake(s: int) -> int:
        await asyncio.sleep(s * 0.01)
        ret.append(s)
        return s

    coros: List[Awaitable[float]] = [
        fake(1),
        fake(2),
        fake(3),
    ]
    done = await asyncx.wait_any(*coros)
    assert ret == [1]
    assert await done == 1

    await asyncio.sleep(0.1)
    assert ret == [1, 2, 3]


@pytest.mark.asyncio
async def test_wait_all_empty() -> None:
    with pytest.raises(ValueError):
        await asyncx.wait_all()


@pytest.mark.asyncio
async def test_wait_all_task() -> None:
    tasks: List[asyncio.Task[None]] = [
        asyncio.create_task(asyncio.sleep(s * 0.01)) for s in range(1, 3)
    ]
    done = await asyncx.wait_all(*tasks)
    assert set(tasks) == set(done)
    assert all(t.done() for t in tasks)


@pytest.mark.asyncio
async def test_wait_all_coro() -> None:
    ret: List[int] = []

    async def fake(s: int) -> int:
        await asyncio.sleep(s * 0.01)
        ret.append(s)
        return s

    coros: List[Awaitable[float]] = [
        fake(1),
        fake(2),
        fake(3),
    ]
    done = await asyncx.wait_all(*coros)
    assert len(done) == 3
    assert {await t for t in done} == {1, 2, 3}
    assert ret == [1, 2, 3]
