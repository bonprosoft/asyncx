from typing import Any, Coroutine, TypeVar

TReturn = TypeVar("TReturn")


def just(ret: TReturn) -> Coroutine[Any, Any, TReturn]:
    async def coro() -> TReturn:
        return ret

    return coro()
