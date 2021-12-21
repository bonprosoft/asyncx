from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from typing import Any, Coroutine, Optional, TypeVar

TReturn = TypeVar("TReturn")
TSelf = TypeVar("TSelf", bound="EventLoopThread")


class EventLoopThread(threading.Thread):
    """An event loop thread that provides thread-safe utility functions.

    .. note::
        The thread cannot be started more than once because of the constraints
        of :class:`threading.Thread`. The class raises :class:`RuntimeError` if
        it is already terminated.

    Example:
        >>> async def _get_ident() -> int:
        ...     return threading.get_ident()
        ...
        >>> thread = EventLoopThread()
        >>> with thread:
        ...     main, sub = await asyncio.gather(
        ...         _get_ident(),
        ...         thread.run_coroutine(_get_ident()),
        ...     )
        >>> main == sub
        False

    """

    def __init__(
        self,
        loop_policy: Optional[asyncio.AbstractEventLoopPolicy] = None,
        daemon: bool = False,
        start: bool = False,
    ) -> None:
        """Creates a new event loop thread.

        Args:
            loop_policy:
                A :obj:`asyncio.AbstractEventLoopPolicy` object to be used
                for creating a new event loop. If :obj:`None` is specified,
                ``asyncio.get_event_loop_policy()`` is used to get the policy.
            daemon:
                If ``True`` is specified, the thread is created with ``daemon=True``.
                Refer to `threading.Thread.daemon`_ for further details.

                .. _threading.Thread.daemon:
                    https://docs.python.org/3/library/threading.html#threading.Thread.daemon
            start:
                If ``True`` is specified, the thread is started immediately.
        """
        self._loop_policy = loop_policy

        self._lock = threading.Lock()
        self._future: concurrent.futures.Future[None] = concurrent.futures.Future()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        super().__init__(target=self._target_impl, daemon=daemon)

        if start:
            self.start()

    def _target_impl(self) -> None:
        future = self._future
        loop: asyncio.AbstractEventLoop
        try:
            loop_policy = self._loop_policy
            if loop_policy is None:
                loop_policy = asyncio.get_event_loop_policy()

            loop = loop_policy.new_event_loop()
        except Exception as ex:
            future.set_exception(ex)

        try:
            self._loop = loop
            future.set_result(None)

            asyncio.set_event_loop(loop)
            loop.run_forever()
        finally:
            self._loop = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get an event loop of the running thread.

        The thread should be running. The method will raise :class:`RuntimeError`
        if the thread is not running.
        """
        loop = self._loop
        if loop is None:
            raise RuntimeError("Thread is not running")
        return loop

    def start(self) -> None:
        """Start the thread and wait for a new event loop to be ready.

        If the thread is already started, it returns immediately.

        Raises:
            RuntimeError:
                If the thread is already terminated.
        """
        with self._lock:
            if self.is_alive():
                return

            if self._future.done():
                raise RuntimeError("threads can only be started once")

            super().start()
            # Wait until loop is created
            self._future.result()

    def shutdown(self, join: bool = True) -> None:
        """Shutdown the running event loop to terminate the thread.

        If the event loop is not running, it returns immediately.

        Args:
            join:
                If `True` is specified, the method waits for the thread to be terminated.

        Raises:
            RumtimeError:
                The method raises a :class:`RuntimeError` if ``join = True`` and the method
                is called by the same thread as ``self.loop`` in order to avoid a deadlock.
                See `threading.Thread.join`_ for further details.

        .. _threading.Thread.join:
            https://docs.python.org/3/library/threading.html#threading.Thread.join
        """
        loop = self._loop
        if loop is None:
            return

        running_loop = loop
        assert isinstance(running_loop, asyncio.AbstractEventLoop)
        running_loop.call_soon_threadsafe(lambda: running_loop.stop())
        if join:
            self.join()

    def __enter__(self: TSelf) -> TSelf:
        """Initialize the event loop if it is not started."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Shutdown the event loop if it is running."""
        self.shutdown()

    def run_coroutine_concurrent(
        self, coro: Coroutine[Any, Any, TReturn]
    ) -> concurrent.futures.Future[TReturn]:
        """Submit a coroutine in the event loop.

        Args:
            coro: A `Coroutine` object to run.

        Returns:
            A :class:`concurrent.future.Future` object that returns the execution result of
            a given coroutine.
        """
        loop = self.loop
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def run_coroutine(
        self,
        coro: Coroutine[Any, Any, TReturn],
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> asyncio.Future[TReturn]:
        """Submit a coroutine in a new thread and waits for its completion in a given ``loop``.

        Args:
            coro: A `Coroutine` object to run.
            loop: An event loop to wait for the completion of ``coro``.

        Returns:
            A :class:`asyncio.Future` object that returns the execution result of a given
            coroutine.
        """
        future = self.run_coroutine_concurrent(coro)
        return asyncio.wrap_future(future, loop=loop)


def run_coroutine_in_thread(
    coro: Coroutine[Any, Any, TReturn],
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Future[TReturn]:
    """Submit a coroutine in a new thread and waits for its completion in a given ``loop``.

    Example:
        >>> async def _get_ident() -> int:
        ...     return threading.get_ident()
        ...
        >>> main, sub = await asyncio.gather(
        ...     _get_ident(),
        ...     asyncx.run_coroutine_in_thread(_get_ident()),
        ... )
        >>> main == sub
        False

    Args:
        coro: A coroutine to run in a new thread.
        loop: An event loop to wait for the completion of ``coro``.

    Returns:
        A :class:`asyncio.Future` object that returns the execution result of
        a given coroutine.
    """

    thread = EventLoopThread(start=True)

    async def impl() -> TReturn:
        try:
            return await coro
        finally:
            thread.shutdown(join=False)

    return thread.run_coroutine(impl(), loop=loop)
