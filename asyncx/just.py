from typing import TypeVar

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
