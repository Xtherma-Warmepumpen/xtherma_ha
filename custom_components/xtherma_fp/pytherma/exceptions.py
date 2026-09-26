"""Exception types raised by the pytherma device library."""


class XthermaError(Exception):
    """Base class for all Xtherma device library exceptions."""


class XthermaModbusError(XthermaError):
    """Exception indicating a Modbus error."""


class XthermaModbusBusyError(XthermaError):
    """Exception indicating busy on Modbus read or write."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Modbus is busy")


class XthermaModbusEmptyDataError(XthermaError):
    """Exception empty data was received via Modbus."""


class XthermaNotConnectedError(XthermaError):
    """Exception indicating the client is not connected."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Not connected error")


class XthermaModbusReadOnlyError(XthermaError):
    """Exception indicating a data is read-only."""
