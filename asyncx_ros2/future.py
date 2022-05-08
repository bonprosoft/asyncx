from __future__ import annotations

import asyncio
import concurrent.futures
from typing import Any, Callable, Optional, Protocol, TypeVar, runtime_checkable

from rclpy.task import Future as ROSFuture

TResult = TypeVar("TResult")
TSelf = TypeVar("TSelf")


@runtime_checkable
class _FutureLikeObject(Protocol[TResult]):
    def cancelled(self) -> bool:
        ...

    def exception(self) -> Optional[BaseException]:
        ...

    def result(self) -> TResult:
        ...

    def set_result(self, result: TResult) -> None:
        ...

    def cancel(self) -> Optional[bool]:
        ...

    def set_exception(self, exception: BaseException) -> None:
        ...

    def done(self) -> bool:
        ...

    def add_done_callback(
        self: TSelf,
        cb: Callable[[TSelf], None],
    ) -> None:
        ...


def _chain_futures(
    src: _FutureLikeObject[TResult],
    src_loop: Optional[asyncio.AbstractEventLoop],
    dest: _FutureLikeObject[TResult],
    dest_loop: Optional[asyncio.AbstractEventLoop],
) -> None:
    def _call_on_loop(
        loop: Optional[asyncio.AbstractEventLoop],
        body: Callable[[], Any],
    ) -> None:
        if loop is not None:
            if loop.is_closed():
                return
            loop.call_soon_threadsafe(body)
        else:
            body()

    def src_to_dest(source: _FutureLikeObject[TResult]) -> None:
        if dest.cancelled() or dest.done():
            return

        assert source.done()
        if source.cancelled():
            _call_on_loop(dest_loop, lambda: dest.cancel())
            return

        exc = source.exception()
        if exc is not None:
            # Capture the current exc instance to avoid mypy error
            exc_ = exc
            _call_on_loop(dest_loop, lambda: dest.set_exception(exc_))
        else:
            result = source.result()
            _call_on_loop(dest_loop, lambda: dest.set_result(result))

    def dest_to_src(destination: _FutureLikeObject[TResult]) -> None:
        if destination.cancelled():
            _call_on_loop(src_loop, lambda: src.cancel())

    src.add_done_callback(src_to_dest)
    dest.add_done_callback(dest_to_src)


def concurrent_to_ros_future(future: concurrent.futures.Future[TResult]) -> ROSFuture:
    """Wrap a :class:`concurrent.futures.Future` object in a :class:`rclpy.task.Future`.

    Args:
        future: A :class:`concurrent.futures.Future` object

    Returns:
        A :class:`rclpy.task.Future` object that wraps the given future
    """
    ros_future = ROSFuture()
    _chain_futures(
        src=future,
        src_loop=None,
        dest=ros_future,
        dest_loop=None,
    )
    return ros_future


def aio_to_ros_future(future: asyncio.Future[TResult]) -> ROSFuture:
    """Wrap a :class:`asyncio.Future` object in a :class:`rclpy.task.Future`.

    Args:
        future: A :class:`asyncio.Future` object

    Returns:
        A :class:`rclpy.task.Future` object that wraps the given future
    """
    ros_future = ROSFuture()
    _chain_futures(
        src=future,
        src_loop=future.get_loop(),
        dest=ros_future,
        dest_loop=None,
    )
    return ros_future


def ros_to_aio_future(
    future: ROSFuture,
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Future[Any]:
    """Wrap a :class:`rclpy.task.Future` object in a :class:`asyncio.Future`.

    Args:
        future: A :class:`rclpy.task.Future` object
        loop: An event loop to wait for the completion of `future`

    Returns:
        A :class:`asyncio.Future` object that wraps the given future
    """
    aio_loop = loop or asyncio.get_running_loop()
    aio_future: asyncio.Future[Any] = asyncio.Future(loop=loop)

    _chain_futures(
        src=future,
        src_loop=None,
        dest=aio_future,
        dest_loop=aio_loop,
    )
    return aio_future


# Utility methods


def ensure_ros_future(future: Any) -> ROSFuture:
    """Wrap an object in a :class:`rclpy.task.Future`.

    Args:
        future:
            A :class:`rclpy.task.Future` object, a :class:`concurrent.futures.Future` object,
            or a :class:`asyncio.Future` object.

    Returns:
        A :class:`rclpy.task.Future` object that wraps the given future
    """
    if isinstance(future, ROSFuture):
        return future
    elif isinstance(future, concurrent.futures.Future):
        return concurrent_to_ros_future(future)
    else:
        assert isinstance(future, asyncio.Future)
        return aio_to_ros_future(future)


def ensure_aio_future(
    coro_or_future: Any,
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Future[Any]:
    """Wrap an object in a :class:`asyncio.Future`.

    Args:
        coro_or_future:
            A :class:`rclpy.task.Future` object or an awaitable object including
            :class:`asyncio.Task`, `asyncio.Future`, and coroutine.
        loop:
            An event loop to wait for the completion of `future`

    Returns:
        A :class:`asyncio.Future` object that wraps the given future
    """
    if isinstance(coro_or_future, ROSFuture):
        return ros_to_aio_future(coro_or_future, loop=loop)
    else:
        return asyncio.ensure_future(coro_or_future, loop=loop)
