import asyncio
import threading

import pytest

import asyncx
from asyncx._types import EventLoopSelector


async def _test_dispatch(selector: EventLoopSelector) -> None:
    async def func() -> int:
        await asyncio.sleep(0.01)
        return threading.get_ident()

    @asyncx.dispatch(selector)
    async def func_dispatch_standard() -> int:
        return await func()

    @asyncx.dispatch(selector)
    async def func_dispatch_no_await() -> int:
        return threading.get_ident()

    base, dispatched = await asyncio.gather(
        func(),
        func_dispatch_standard(),
    )
    assert base != dispatched
    assert dispatched == await func_dispatch_no_await()


@pytest.mark.asyncio
async def test_dispatch() -> None:
    with asyncx.EventLoopThread() as thread:
        await _test_dispatch(thread.loop)

    with asyncx.EventLoopThread() as thread:
        await _test_dispatch(thread.get_loop)
