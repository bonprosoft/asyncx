import asyncio
from typing import Any, Callable, Coroutine, TypeVar, Union

TAsyncCallable = TypeVar(
    "TAsyncCallable", bound=Callable[..., Coroutine[Any, Any, Any]]
)
TReturn = TypeVar("TReturn")
EventLoopSelector = Union[
    asyncio.AbstractEventLoop,
    Callable[[], asyncio.AbstractEventLoop],
]
