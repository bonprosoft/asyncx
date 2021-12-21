import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar, cast

TAsyncCallable = TypeVar("TAsyncCallable", bound=Callable[..., Awaitable[Any]])


def shield(func: TAsyncCallable) -> TAsyncCallable:
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

    Args:
        func: An async function to be shielded.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await asyncio.shield(func(*args, **kwargs))

    return cast(TAsyncCallable, wrapper)
