from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from typing import Any, Coroutine, Optional, TypeVar

TReturn = TypeVar("TReturn")
TSelf = TypeVar("TSelf", bound="EventLoopThread")


class EventLoopThread(threading.Thread):
    def __init__(
        self,
        loop_policy: Optional[asyncio.AbstractEventLoopPolicy] = None,
        daemon: bool = False,
        start: bool = False,
    ) -> None:
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
        loop = self._loop
        if loop is None:
            raise RuntimeError("Thread is not running")
        return loop

    def start(self) -> None:
        with self._lock:
            if self.is_alive():
                return

            # NOTE: The following constraint is from threading.Thread
            if self._future.done():
                raise RuntimeError("threads can only be started once")

            super().start()
            # Wait until loop is created
            self._future.result()

    def shutdown(self, join: bool = True) -> None:
        loop = self._loop
        if loop is None:
            return

        running_loop = loop
        assert isinstance(running_loop, asyncio.AbstractEventLoop)
        running_loop.call_soon_threadsafe(lambda: running_loop.stop())
        if join:
            self.join()

    def __enter__(self: TSelf) -> TSelf:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.shutdown()

    def run_coroutine_concurrent(
        self, coro: Coroutine[Any, Any, TReturn]
    ) -> concurrent.futures.Future[TReturn]:
        loop = self.loop
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def run_coroutine(
        self,
        coro: Coroutine[Any, Any, TReturn],
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> asyncio.Future[TReturn]:
        future = self.run_coroutine_concurrent(coro)
        return asyncio.wrap_future(future, loop=loop)


def run_coroutine_in_thread(
    coro: Coroutine[Any, Any, TReturn],
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Future[TReturn]:
    thread = EventLoopThread(start=True)

    async def impl() -> TReturn:
        try:
            return await coro
        finally:
            thread.shutdown(join=False)

    return thread.run_coroutine(impl(), loop=loop)
