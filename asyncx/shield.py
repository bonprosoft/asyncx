import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar, cast

TReturn = TypeVar("TReturn")
AsyncCallable = Callable[..., Awaitable[TReturn]]


def shield(func: AsyncCallable[TReturn]) -> AsyncCallable[TReturn]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> TReturn:
        return await asyncio.shield(func(*args, **kwargs))

    return cast(AsyncCallable[TReturn], wrapper)
