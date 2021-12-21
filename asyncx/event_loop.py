import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar, Union, cast

EventLoopSelector = Union[
    asyncio.AbstractEventLoop,
    Callable[[], asyncio.AbstractEventLoop],
]
TAsyncCallable = TypeVar("TAsyncCallable", bound=Callable[..., Awaitable[Any]])


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
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            target_loop: asyncio.AbstractEventLoop
            if callable(loop_selector):
                target_loop = loop_selector()
            else:
                target_loop = loop_selector

            coro = func(*args, **kwargs)

            caller_loop = asyncio.get_event_loop()
            if caller_loop == target_loop:
                return await coro
            else:
                f = asyncio.run_coroutine_threadsafe(coro, target_loop)
                try:
                    return await asyncio.wrap_future(f, loop=caller_loop)
                finally:
                    # If the caller task was cancelled, propagate its cancellation
                    # to inner future
                    if f.running():
                        f.cancel()

        return cast(TAsyncCallable, wrapper)

    return deco
