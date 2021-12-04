from __future__ import annotations

import asyncio
import contextlib
from typing import Any, AsyncContextManager, AsyncIterator, Awaitable, TypeVar, overload

TReturn = TypeVar("TReturn")
TFuture = TypeVar("TFuture", bound="asyncio.Future[Any]")


@overload
def acontext(
    coro: Awaitable[TReturn],
) -> AsyncContextManager[asyncio.Task[TReturn]]:
    ...


@overload
def acontext(future: TFuture) -> AsyncContextManager[TFuture]:
    ...


@contextlib.asynccontextmanager
async def acontext(
    coro_or_future: Awaitable[TReturn],
) -> AsyncIterator[asyncio.Future[TReturn]]:
    future: asyncio.Future[TReturn] = asyncio.ensure_future(coro_or_future)
    try:
        yield future
    finally:
        future.cancel()
