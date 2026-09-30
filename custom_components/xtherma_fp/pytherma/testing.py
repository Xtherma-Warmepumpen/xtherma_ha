"""Shipped test-support module providing an in-memory Modbus unit.

Analogous to ``aiohttp.test_utils``: :class:`FakeUnit` is an in-memory
structural implementation of the :class:`modbus_connection.ModbusUnit`
protocol, backed by a flat register image. It records every read and write
call and supports scripting per-call results, so
:class:`~pytherma.device.XthermaFP` behaviour can be exercised without
a real transport or backend.

Only the holding-register operations used by :class:`XthermaFP` are
functional; all other protocol members raise :exc:`NotImplementedError`.

Example::

    from pytherma import XthermaFP
    from pytherma.addresses import MODBUS_REGISTER_SIZE
    from pytherma.testing import FakeUnit

    unit = FakeUnit(image=[0] * MODBUS_REGISTER_SIZE)
    device = XthermaFP(unit)
"""

from collections.abc import Callable

from modbus_connection import ModbusUnit

from .addresses import MODBUS_REGISTER_SIZE


class FakeUnit(ModbusUnit):
    """In-memory Modbus unit with a register image and scripted results.

    By default :meth:`read_holding_registers` returns slices of a flat
    register image; a scripted per-call result may be queued instead (see
    :meth:`queue_read_result`). :meth:`write_register` stores the value in
    the image and records the call. Every read (including one whose scripted
    result is an ``Exception``) and every successful write is
    appended to :attr:`read_calls` / :attr:`write_calls` as
    ``(unit_id, address, ...)``.

    Args:
        image: flat register image; defaults to all zeros.
        unit_id: the slave (unit) id this handle is bound to; recorded in
            every call tuple (a real handle carries it via
            ``connection.for_unit(unit_id)``).
    """

    def __init__(
        self,
        image: list[int] | None = None,
        *,
        unit_id: int = 1,
    ) -> None:
        """Class constructor."""
        self.unit_id = unit_id
        self._connected = True
        self.closed = False
        self.image = list(image) if image is not None else [0] * MODBUS_REGISTER_SIZE
        #: scripted read results, in call order; ``None`` falls back to the image
        self._read_queue: list[list[int] | Exception | None] = []
        #: exceptions to raise on the next write, in call order
        self._write_errors: list[Exception | None] = []
        #: recorded (unit_id, address, count) read calls
        self.read_calls: list[tuple[int, int, int]] = []
        #: recorded (unit_id, address, value) write calls
        self.write_calls: list[tuple[int, int, int]] = []

    @property
    def connected(self) -> bool:
        """Whether the unit's link is connected."""
        return self._connected

    def queue_read_result(self, result: list[int] | Exception | None) -> None:
        """Queue the result of the next read, in call order.

        Args:
            result: ``list[int]`` to return as the register values (should
                match the requested count), an ``Exception`` to raise, or
                ``None`` to fall back to the register image.
        """
        self._read_queue.append(result)

    def queue_write_error(self, error: Exception | None) -> None:
        """Queue the exception to raise on the next write (``None``: no error)."""
        self._write_errors.append(error)

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read ``count`` holding registers starting at ``address``."""
        if self._read_queue:
            result = self._read_queue.pop(0)
            if result is not None:
                self.read_calls.append((self.unit_id, address, count))
                if isinstance(result, Exception):
                    raise result
                return list(result)
        self.read_calls.append((self.unit_id, address, count))
        return list(self.image[address : address + count])

    async def write_register(self, address: int, value: int) -> None:
        """Write ``value`` to a single holding register."""
        if self._write_errors:
            error = self._write_errors.pop(0)
            if error is not None:
                raise error
        self.image[address] = value
        self.write_calls.append((self.unit_id, address, value))

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_input_registers")
        raise err

    async def write_registers(self, address: int, values: list[int]) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support write_registers")
        raise err

    async def read_coils(self, address: int, count: int) -> list[bool]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_coils")
        raise err

    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_discrete_inputs")
        raise err

    async def write_coil(self, address: int, value: bool) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support write_coil")
        raise err

    async def write_coils(self, address: int, values: list[bool]) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support write_coils")
        raise err

    async def read_exception_status(self) -> int:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_exception_status")
        raise err

    async def report_server_id(self) -> bytes:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support report_server_id")
        raise err

    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support mask_write_register")
        raise err

    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_write_registers")
        raise err

    async def read_fifo_queue(self, address: int) -> list[int]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_fifo_queue")
        raise err

    async def read_device_identification(self) -> dict[int, bytes]:
        """Unsupported operation."""
        err = NotImplementedError(
            "FakeUnit does not support read_device_identification"
        )
        raise err

    async def read_file_record(self, file: int, record: int, length: int) -> list[int]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support read_file_record")
        raise err

    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support write_file_record")
        raise err

    async def diagnostics(self, sub_function: int, data: int = 0) -> int:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support diagnostics")
        raise err

    async def get_comm_event_counter(self) -> tuple[bool, int]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support get_comm_event_counter")
        raise err

    async def get_comm_event_log(self) -> bytes:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support get_comm_event_log")
        raise err

    def set_message_spacing(self, seconds: float) -> None:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support set_message_spacing")
        raise err

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Unsupported operation."""
        err = NotImplementedError("FakeUnit does not support on_connection_lost")
        raise err

    async def disconnect(self) -> None:
        """Disconnect the unit (recycles the link)."""
        self._connected = False
        self.closed = True
