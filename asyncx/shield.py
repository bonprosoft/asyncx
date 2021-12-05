import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar, cast

TReturn = TypeVar("TReturn")
AsyncCallable = Callable[..., Awaitable[TReturn]]


def shield(func: AsyncCallable[TReturn]) -> AsyncCallable[TReturn]:
    """A decorator for an async function to protect it from being cancelled.

    Example:
        >>> @asyncx.shield
        ... async def foo() -> None:
        ...     print("Start foo")
        ...     await asyncio.sleep(1)
        ...     print("End foo")
        >>> coro = asyncio.create_task(foo())
        >>> await asyncio.sleep(0.1)
        Start foo
        >>> coro.cancel()
        >>> await asyncio.sleep(1)
        End foo

    Arg:
        func: An async function to be shielded.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> TReturn:
        return await asyncio.shield(func(*args, **kwargs))

    return cast(AsyncCallable[TReturn], wrapper)
