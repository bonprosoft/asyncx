import asyncio
import itertools
import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import SetBool

import asyncx
import asyncx_ros2

_thread = asyncx.EventLoopThread()
SERVICE_NAME = "example_add"


class NodeBase(Node):
    def __init__(self, node_name: str) -> None:
        super().__init__(node_name)
        self._name = node_name
        self._thread = threading.Thread(target=self._spin)
        self._executor = SingleThreadedExecutor()

    def _spin(self) -> None:
        rclpy.spin(self, executor=self._executor)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        print(f"Stopping node: {self._name}")
        self._executor.shutdown(timeout_sec=0.1)


class Server(NodeBase):
    def __init__(self) -> None:
        super().__init__("server")
        self._server = self.create_service(
            SetBool,
            SERVICE_NAME,
            self._set_bool,
            callback_group=ReentrantCallbackGroup(),
        )
        self._counter = itertools.count()

    @asyncx_ros2.wrap_as_ros_coroutine(_thread.get_loop)
    async def _set_bool(
        self, request: SetBool.Request, response: SetBool.Response
    ) -> SetBool.Response:
        stime = time.time()

        val = next(self._counter)
        self.get_logger().info(f"counter={val}, get request")
        await asyncio.sleep(1.0)
        elapsed = time.time() - stime
        self.get_logger().info(f"counter={val}, return response (elapsed: {elapsed})")
        return response


class Client(NodeBase):
    def __init__(self) -> None:
        super().__init__("client")
        self._client = self.create_client(
            SetBool,
            SERVICE_NAME,
            callback_group=ReentrantCallbackGroup(),
        )
        self._timer = self.create_timer(
            0.5,
            self.timer_callback,
            callback_group=ReentrantCallbackGroup(),
        )
        self._counter = itertools.count()

    def run(self) -> None:
        executor = SingleThreadedExecutor()
        rclpy.spin(self, executor=executor)

    async def _get_request(self, val: int) -> SetBool.Request:
        request = SetBool.Request()
        request.data = val % 2 == 0
        await asyncio.sleep(1.0)
        return request

    @asyncx_ros2.wrap_as_ros_coroutine(_thread.get_loop)
    async def timer_callback(self) -> None:
        stime = time.time()
        val = next(self._counter)
        self.get_logger().info(f"counter={val}, timer callback")
        request = await self._get_request(val)
        self.get_logger().info(f"counter={val}, send request")
        await asyncx_ros2.ensure_aio_future(self._client.call_async(request))
        elapsed = time.time() - stime
        self.get_logger().info(f"counter={val}, completed (elapsed: {elapsed})")


def main() -> None:
    rclpy.init()

    with _thread:
        print("Press enter to stop")
        server = Server()
        client = Client()
        server.start()
        client.start()

        try:
            input()
        finally:
            print("Terminating nodes")
            client.stop()
            server.stop()
            server.destroy_node()
            client.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
