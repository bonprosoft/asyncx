import asyncio
from typing import Any, Awaitable, Sequence


async def wait_any(*awaitables: Awaitable[Any]) -> Awaitable[Any]:
    if len(awaitables) == 0:
        raise ValueError("awaitables cannot be empty")
    completed, pending = await asyncio.wait(
        awaitables,
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert len(completed) >= 1
    return list(completed)[0]


async def wait_all(*awaitables: Awaitable[Any]) -> Sequence[Awaitable[Any]]:
    if len(awaitables) == 0:
        raise ValueError("awaitables cannot be empty")
    completed, pending = await asyncio.wait(
        awaitables,
        return_when=asyncio.ALL_COMPLETED,
    )
    assert len(pending) == 0
    return list(completed)
