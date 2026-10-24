"""Common definitions for Xtherma client variants."""

from abc import ABC, abstractmethod
from datetime import timedelta

from homeassistant.helpers.entity import EntityDescription

from .pytherma.exceptions import XthermaError


class XthermaRestBusyError(XthermaError):
    """Exception indicating busy on REST API read."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("REST API is busy")


class XthermaRestApiError(XthermaError):
    """Exception indicating a REST API error."""

    def __init__(self, code: int) -> None:
        """Class constructor."""
        super().__init__()
        self.code = code


class XthermaRestMalformedError(XthermaError):
    """Exception indicating a malformed REST API response."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("malformed REST API response")


class XthermaReadOnlyError(XthermaError):
    """Exception indicating a data is read-only."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__()


class XthermaTimeoutError(XthermaError):
    """Exception indicating a communication timeout."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("timeout")


class XthermaClient(ABC):
    """Base class for Xtherma clients."""

    @abstractmethod
    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        """Connect client to server endpoint."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect client."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_data(self) -> dict[str, int | float]:
        """Obtain fresh data."""
        raise NotImplementedError

    @abstractmethod
    async def async_put_data(self, value: int | float, desc: EntityDescription) -> None:
        """Write data."""
        raise NotImplementedError

    @abstractmethod
    def write_windows(
        self, desc: EntityDescription
    ) -> tuple[timedelta, timedelta] | None:
        """Return the write timing windows for ``desc``.

        The tuple holds ``(read_hold, write_throttle)``: how long the
        read-back is considered stale after an accepted write, and how long
        the device silently discards repeated writes. ``None`` when the
        transport does not accept writes at all.
        """
        raise NotImplementedError

    @abstractmethod
    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        raise NotImplementedError
