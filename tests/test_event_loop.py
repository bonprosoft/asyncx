import asyncio
import threading

import pytest

import asyncx


@pytest.mark.asyncio
async def test_dispatch() -> None:
    with asyncx.EventLoopThread() as thread:

        async def func() -> int:
            await asyncio.sleep(0.01)
            return threading.get_ident()

        @asyncx.dispatch(thread.loop)
        async def func_dispatch() -> int:
            return await func()

        main, sub = await asyncio.gather(func(), func_dispatch())

    assert main != sub


@pytest.mark.asyncio
async def test_dispatch_callable() -> None:
    def get_event_loop() -> asyncio.AbstractEventLoop:
        return thread.loop

    async def func() -> int:
        await asyncio.sleep(0.01)
        return threading.get_ident()

    @asyncx.dispatch(get_event_loop)
    async def func_dispatch() -> int:
        return await func()

    with asyncx.EventLoopThread() as thread:
        main, sub = await asyncio.gather(func(), func_dispatch())

    assert main != sub
