.. module:: asyncx

*************
API Reference
*************

* :ref:`genindex`
* :ref:`modindex`

----

Coroutine Factory
----------------------
.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx.just
   asyncx.wait_any
   asyncx.wait_all


Shielding
-------------------

.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx.shield


Context Manager
----------------------

.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx.acontext


Thread Handling
----------------------

.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx.EventLoopThread
   asyncx.run_coroutine_in_thread


Event Loop
----------------------

.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx.dispatch
   asyncx.dispatch_coroutine


ROS2 Support (rclpy)
--------------------

.. module:: asyncx_ros2
.. autosummary::
   :nosignatures:
   :toctree: generated/

   asyncx_ros2.aio_to_ros_future
   asyncx_ros2.concurrent_to_ros_future
   asyncx_ros2.ros_to_aio_future
   asyncx_ros2.ensure_aio_future
   asyncx_ros2.ensure_ros_future
   asyncx_ros2.wrap_as_ros_coroutine
