import asyncio
import threading
from typing import Iterator

import pytest

import asyncx


async def _get_ident() -> int:
    # await 0.01 seconds to test event loop
    await asyncio.sleep(0.01)
    return threading.get_ident()


@pytest.fixture
def event_loop_thread() -> Iterator[asyncx.EventLoopThread]:
    thread = asyncx.EventLoopThread()
    try:
        yield thread
    finally:
        thread.shutdown()


@pytest.mark.asyncio
async def test_event_loop_thread(event_loop_thread: asyncx.EventLoopThread) -> None:
    assert not event_loop_thread.is_alive()
    with pytest.raises(RuntimeError):
        event_loop_thread.loop

    coro = _get_ident()
    with pytest.raises(RuntimeError):
        event_loop_thread.run_coroutine(coro)
    coro.close()

    event_loop_thread.start()
    assert event_loop_thread.is_alive()
    assert event_loop_thread.loop is not None
    main, sub = await asyncio.gather(
        _get_ident(),
        event_loop_thread.run_coroutine(_get_ident()),
    )
    assert isinstance(main, int)
    assert isinstance(sub, int)
    # Assert that coroutine is executed in different event loops
    assert main != sub

    event_loop_thread.shutdown()
    assert not event_loop_thread.is_alive()

    with pytest.raises(RuntimeError):
        event_loop_thread.loop

    coro = _get_ident()
    with pytest.raises(RuntimeError):
        event_loop_thread.run_coroutine(coro)
    coro.close()


@pytest.mark.asyncio
async def test_event_loop_thread_start() -> None:
    event_loop_thread = asyncx.EventLoopThread(start=True)
    try:
        assert event_loop_thread.is_alive()
        assert event_loop_thread.loop is not None
        thread_id = await event_loop_thread.run_coroutine(_get_ident())
        assert thread_id != await _get_ident()
    finally:
        event_loop_thread.shutdown()


@pytest.mark.asyncio
async def test_run_coroutine_in_thread() -> None:
    main, sub = await asyncio.gather(
        _get_ident(),
        asyncx.run_coroutine_in_thread(_get_ident()),
    )
    assert main != sub
