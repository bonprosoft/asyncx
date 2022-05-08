import asyncio
import functools
from typing import Any, Callable, cast

from asyncx._types import EventLoopSelector, TAsyncCallable

from .future import concurrent_to_ros_future


def wrap_as_ros_coroutine(
    loop_selector: EventLoopSelector,
) -> Callable[[TAsyncCallable], TAsyncCallable]:
    """A decorator to wrap an async function running on an asyncio event loop
    with a :class:`rclpy.task.Future`.

    Example:
        >>> @asyncx_ros2.wrap_as_ros_coroutine(get_event_loop)
        ... async def foo() -> None:
        ...     await asyncio.sleep(1)
        ...     print("Called!")
        ...
        >>> node.create_timer(0.5, foo)

    Args:
        loop_selector:
            An event loop on which a coroutine runs.
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
            f = asyncio.run_coroutine_threadsafe(coro, target_loop)
            return await concurrent_to_ros_future(f)

        return cast(TAsyncCallable, wrapper)

    return deco
