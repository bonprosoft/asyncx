import asyncio
from typing import Any, Awaitable, Sequence, TypeVar

TReturn = TypeVar("TReturn")


async def just(ret: TReturn) -> TReturn:
    """Creates a coroutine that returns a specified result.

    Example:
        >>> await asyncx.just(42)
        42

    Args:
        ret: The result to return from a coroutine

    Returns:
        A :class:`Coroutine[Any, Any, T]` object that returns ``ret``.
    """

    return ret


async def wait_any(*awaitables: Awaitable[Any]) -> Awaitable[Any]:
    """Creates a coroutine that waits for any of given awaitables to be completed.

    Example:
        >>> coro1 = asyncio.create_task(asyncio.sleep(1))
        >>> coro2 = asyncio.create_task(asyncio.sleep(2))
        >>> await asyncx.wait_any(coro1, coro2) is coro1
        True

    Args:
        awaitables: Awaitable objects to wait.

    Returns:
        A :class:`Coroutine` object that returns first finished :class:`asyncio.Future` object.
    """

    if len(awaitables) == 0:
        raise ValueError("awaitables cannot be empty")
    completed, pending = await asyncio.wait(
        awaitables,
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert len(completed) >= 1
    return list(completed)[0]


async def wait_all(*awaitables: Awaitable[Any]) -> Sequence[Awaitable[Any]]:
    """Creates a coroutine that waits for all of given awaitables to be completed.

    Example:
        >>> coro1 = asyncio.create_task(asyncio.sleep(1))
        >>> coro2 = asyncio.create_task(asyncio.sleep(2))
        >>> ret = await asyncx.wait_all(coro1, coro2)
        >>> set(ret) == {coro1, coro2}
        True

    Args:
        awaitables: Awaitable objects to wait.

    Returns:
        A :class:`Coroutine` object that returns a list of completed
        :class:`asyncio.Future` object.
    """

    if len(awaitables) == 0:
        raise ValueError("awaitables cannot be empty")
    completed, pending = await asyncio.wait(
        awaitables,
        return_when=asyncio.ALL_COMPLETED,
    )
    assert len(pending) == 0
    return list(completed)
