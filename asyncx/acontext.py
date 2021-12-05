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
    awaitable: Awaitable[TReturn],
) -> AsyncIterator[asyncio.Future[TReturn]]:
    """Creates an async context manager that cancels a given awaitable in ``__aexit__``.

    Arg:
        awaitable: A target awaitable object

    Returns:
        An async context manager that creates a future and cancels it of a given awaitable.
    """
    future: asyncio.Future[TReturn] = asyncio.ensure_future(awaitable)
    try:
        yield future
    finally:
        future.cancel()
