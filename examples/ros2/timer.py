import asyncio
import itertools
import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node

import asyncx
import asyncx_ros2

_thread = asyncx.EventLoopThread()


class TimerNode(Node):
    def __init__(self) -> None:
        super().__init__("timer")
        self._timer = self.create_timer(
            0.5, self.timer_callback, callback_group=ReentrantCallbackGroup()
        )
        self._counter = itertools.count()
        self._node_ident = threading.get_ident()

    @asyncx_ros2.wrap_as_ros_coroutine(_thread.get_loop)
    async def timer_callback(self) -> None:
        assert threading.get_ident() != self._node_ident
        val = next(self._counter)
        stime = time.time()
        await asyncio.sleep(1.0)
        elapsed = time.time() - stime
        self.get_logger().info(f"Message: {val}, Elapsed: {elapsed}")


def main() -> None:
    rclpy.init()
    with _thread:
        node = TimerNode()
        rclpy.spin(node)
        node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
