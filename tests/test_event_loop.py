import asyncio
import threading
from typing import Tuple

import pytest

import asyncx
from asyncx._types import EventLoopSelector


async def _test_dispatch(selector: EventLoopSelector) -> Tuple[int, int]:
    async def func() -> int:
        await asyncio.sleep(0.01)
        return threading.get_ident()

    @asyncx.dispatch(selector)
    async def func_dispatch_standard() -> int:
        return await func()

    @asyncx.dispatch(selector)
    async def func_dispatch_no_await() -> int:
        return threading.get_ident()

    base, dispatched, dispatched_no_await = await asyncio.gather(
        func(),
        func_dispatch_standard(),
        func_dispatch_no_await(),
    )
    assert dispatched == dispatched_no_await
    return base, dispatched


@pytest.mark.asyncio
async def test_dispatch() -> None:
    loop = asyncio.get_running_loop()

    with asyncx.EventLoopThread() as thread:
        base, dispatched = await _test_dispatch(thread.loop)
        assert base != dispatched

        base, dispatched = await _test_dispatch(thread.loop)
        assert base != dispatched

        base, dispatched = await _test_dispatch(loop)
        assert base == dispatched


@pytest.mark.asyncio
async def test_dispatch_coroutine() -> None:
    async def func() -> int:
        await asyncio.sleep(0.01)
        return threading.get_ident()

    with asyncx.EventLoopThread() as thread:
        base_loop = asyncio.get_running_loop()
        base = await func()

        dispatched = await asyncx.dispatch_coroutine(
            func(),
            target_loop=thread.loop,
        )
        assert base != dispatched

        dispatched = await asyncx.dispatch_coroutine(
            func(),
            target_loop=base_loop,
        )
        assert base == dispatched

        # coro1: Run `func()` on `base_loop` and wait for the result on `thread.loop`.
        # coro2: Run `coro` on `thread.loop` and wait for the result on `base_loop`.
        coro1 = asyncx.dispatch_coroutine(
            func(),
            target_loop=base_loop,
            caller_loop=thread.loop,
        )
        coro2 = asyncx.dispatch_coroutine(
            coro1,
            target_loop=thread.loop,
            caller_loop=base_loop,
        )
        assert base == await coro2
