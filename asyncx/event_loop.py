import asyncio
import functools
from typing import Any, Callable, Coroutine, Optional, cast

from ._types import EventLoopSelector, TAsyncCallable, TReturn


def dispatch(
    loop_selector: EventLoopSelector,
) -> Callable[[TAsyncCallable], TAsyncCallable]:
    """A decorator to dispatch an async function to another event loop.

    Example:
        >>> async def foo() -> None:
        ...     return threading.get_ident()
        ...
        >>> @asyncx.dispatch(get_event_loop)
        ... async def foo_dispatch() -> None:
        ...     return threading.get_ident()
        ...
        >>> current, dispatched = await asyncio.gather(
        ...     foo(), foo_dispatch(),
        ... )
        >>> current != dispatched
        True

    Args:
        loop_selector:
            Target event loop to which a coroutine is dispatched.
            The value must be either an event loop or a callable that returns
            an event loop.
    """

    def deco(func: TAsyncCallable) -> TAsyncCallable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> TReturn:
            target_loop: asyncio.AbstractEventLoop
            if callable(loop_selector):
                target_loop = loop_selector()
            else:
                target_loop = loop_selector

            caller_loop = asyncio.get_running_loop()
            coro = func(*args, **kwargs)
            return await dispatch_coroutine(
                coro,
                target_loop=target_loop,
                caller_loop=caller_loop,
            )

        return cast(TAsyncCallable, wrapper)

    return deco


async def dispatch_coroutine(
    coro: Coroutine[Any, Any, TReturn],
    target_loop: asyncio.AbstractEventLoop,
    caller_loop: Optional[asyncio.AbstractEventLoop] = None,
) -> TReturn:
    """Execute the specified coroutine on the specified event loop.

    Example:
        >>> async def foo() -> None:
        ...     return threading.get_ident()
        ...
        >>> current, dispatched = await asyncio.gather(
        ...     foo(),
        ...     asyncx.dispatch_coroutine(foo(), other_loop),
        ... )
        >>> current != dispatched
        True

    Args:
        coro:
            A coroutine to be dispatched.
        target_loop:
            An event loop to execute the ``coro``.
        caller_loop:
            An event loop to wait for dispatched coroutine to complete.
    """
    if caller_loop is None:
        caller_loop = asyncio.get_running_loop()

    if target_loop == caller_loop:
        return await coro

    f = asyncio.run_coroutine_threadsafe(coro, target_loop)
    return await asyncio.wrap_future(f, loop=caller_loop)
