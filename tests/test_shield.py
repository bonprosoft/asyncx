import asyncio
from typing import List

import pytest

import asyncx


@pytest.mark.asyncio
async def test_shield() -> None:
    ret: List[int] = []
    join = asyncio.Event()

    @asyncx.shield
    async def fake(value: int, prefix: str = "default") -> str:
        await join.wait()
        join.clear()
        ret.append(value)
        return f"{prefix}-{value}"

    join.set()
    assert await fake(1) == "default-1"
    assert ret == [1]

    join.set()
    assert await fake(2, prefix="foo") == "foo-2"
    assert ret == [1, 2]

    task = asyncio.create_task(fake(3, "bar"))
    # sleep 0.01 second to ensure task is running
    await asyncio.sleep(0.01)
    assert not task.done()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert task.done()
    assert task.cancelled()

    # assert that fake() is running as it is shielded
    join.set()
    await asyncio.sleep(0.01)
    assert ret == [1, 2, 3]
