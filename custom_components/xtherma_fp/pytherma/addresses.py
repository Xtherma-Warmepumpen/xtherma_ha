"""Register address layout for the Xtherma FP Modbus interface."""

from dataclasses import dataclass

from .bindings import MODBUS_BINDING_BY_KEY


@dataclass(frozen=True, slots=True)
class RegisterRange:
    """Definition of a register range which is read in one call."""

    # first and last register of this range
    first_reg: int
    # last register of this range
    last_reg: int

    # a register in this range which cannot ever be empty
    # this is used to detect bogus reads where the device sends us
    # empty data instead of, for instance, a busy response.
    non_empty_reg: int

    @property
    def length(self) -> int:
        """Number of registers in this range."""
        return self.last_reg - self.first_reg + 1


# The modbus protocol only allows reading up to 125 registers at once.
# Therefore, we need to split the entire register range into
# manageable sub ranges.
# The non-empty anchors reference bindings by quantity key, not magic
# addresses: register 501 (range 0) and controller_v (range 1) can never
# read as empty.
REGISTER_RANGES: tuple[RegisterRange, ...] = (
    RegisterRange(
        first_reg=0,
        last_reg=71,
        non_empty_reg=MODBUS_BINDING_BY_KEY["501"].address,
    ),
    RegisterRange(
        first_reg=100,
        last_reg=193,
        non_empty_reg=MODBUS_BINDING_BY_KEY["controller_v"].address,
    ),
)

# The total size of the modbus register space used.
MODBUS_REGISTER_SIZE: int = REGISTER_RANGES[-1].last_reg + 1
