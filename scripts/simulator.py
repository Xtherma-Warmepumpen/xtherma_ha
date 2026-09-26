"""Simple Modbus TCP server using pymodbus SimDevice simulator and trace hooks."""

import asyncio

from pymodbus.pdu import ModbusPDU
from pymodbus.server import StartAsyncTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice


def _trace_pdu(to_send: bool, pdu: ModbusPDU) -> ModbusPDU:
    """Trace incoming or outgoing Protocol Data Units."""
    direction = "TX" if to_send else "RX"
    print(f"[TRACE] {direction} PDU: {pdu}")
    return pdu


def _trace_connect(connected: bool) -> None:
    """Trace client connection/disconnection events."""
    state = "Connected" if connected else "Disconnected"
    print(f"[TRACE] Client state change: {state}")


async def _main() -> None:
    # Initialize 256 holding registers (values 0 to 255) for Device ID 1
    device = SimDevice(
        id=1,
        simdata=SimData(
            address=0,
            values=list(range(256)),
            datatype=DataType.REGISTERS,
        ),
    )

    print("[TRACE] Starting pymodbus TCP server on 127.0.0.1:5020...")

    # Start the server passing the SimDevice context and trace options directly
    await StartAsyncTcpServer(
        context=device,
        address=("127.0.0.1", 5020),
        trace_pdu=_trace_pdu,
        trace_connect=_trace_connect,
    )


if __name__ == "__main__":
    asyncio.run(_main())
