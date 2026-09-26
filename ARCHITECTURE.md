# Architecture

This file describes stable repository structure and application architecture.

It should change relatively infrequently.

## Repository Layout

Document the major directories and their responsibilities.

```text
.
├── AGENTS.md              # Agent operating instructions
├── ARCHITECTURE.md        # Stable architectural map (this file)
├── CONTEXT.md             # Current execution state
├── DECISIONS.md           # Durable technical decisions
├── custom_components/
│   └── xtherma_fp/        # The integration (see Architectural Map)
│       ├── pytherma/      # Vendored device library (quantity/binding model + device accessor)
│       ├── translations/  # UI translations (en, de)
│       └── vendor/        # Deprecated: vendored pymodbus (dead since D4; deletion pending)
├── scripts/               # Developer tooling: setup, develop, lint, release
├── tests/                 # Pytest suite (see Testing Architecture)
├── config/                # Development Home Assistant instance state
└── configuration.yaml     # Development instance config (debug logging)
```

## Architectural Map

- **Entry Point**: [`__init__.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/__init__.py) handles setup, unloading, and entity migration.
- **Configuration**: [`config_flow.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/config_flow.py) manages REST/Modbus setup and validation.
- **Data Orchestration**: [`coordinator.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/coordinator.py) implements `DataUpdateCoordinator` with write-blocking logic to prevent stale data overwrites.
- **Base Entity**: [`entity.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/entity.py) provides `XthermaCoordinatorEntity` for shared `unique_id` and icon logic.
- **Platform Implementations**:
    - [`sensor.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/sensor.py)
    - [`binary_sensor.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/binary_sensor.py)
    - [`switch.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/switch.py)
    - [`number.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/number.py)
    - [`select.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/select.py)

## Transport Layer
- **Abstraction**: [`xtherma_client_common.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/xtherma_client_common.py) defines the `XthermaClient` ABC + `_FACTORS`/`_RFACTORS` scaling.
- **REST Client**: [`xtherma_client_rest.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/xtherma_client_rest.py) (Read-only via Fernportal).
- **Modbus Client**: [`xtherma_client_modbus.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/xtherma_client_modbus.py) — thin wrapper over the library's `XthermaFP` on a pre-bound `modbus_connection.ModbusUnit` handle; owns no transport or lifecycle (D4).
- **Unit acquisition**: `__init__.py` (setup) obtains the unit via `homeassistant.components.modbus.async_get_unit`; `config_flow.py` probes via `async_get_temporary_unit`. Holders of the same `host:port` share one serialized connection; the `modbus` integration owns the link and closes it when the last holding entry unloads.
- **Boundary**: All direct Modbus I/O lives in the `pytherma` library (`XthermaFP`); the integration's mock boundary is `tests/conftest.py` patching `custom_components.xtherma_fp.async_get_unit` with the library's in-memory `FakeUnit`. All other files consume the client via the `XthermaClient` ABC.

## Data Models & IDL Schema
- **Entity Definitions**: [`entity_descriptors.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/entity_descriptors.py) composes the library's binding tables (`MODBUS_BINDINGS` / `REST_BINDINGS`) × `entity_mapping.RENDERINGS` → `MODBUS_DESCRIPTORS` + `ENTITY_DESCRIPTIONS` (explicit REST order).
- **Constants**: [`const.py`](/workspaces/xtherma_ha/custom_components/xtherma_fp/const.py) contains domain keys and REST rate-limit/timeout.
- **Quantity/Binding Model**: lives in the library (`pytherma`: `data_model.py`, `quantities.py` + `quantities_settings.py`/`quantities_telemetry.py` rows, `bindings.py`, `addresses.py`); quantities hold transport-neutral semantics (D5), `bindings.py` resolves pure key-reference tables (`_MODBUS_ROWS`, `_REST_QUANTITY_KEYS`) onto them; `REGISTER_RANGES` / `MODBUS_REGISTER_SIZE` come from `pytherma.addresses`.

## Data Flow

`config_flow` → `__init__.async_setup_entry` builds the client → `XthermaDataUpdateCoordinator` polls `client.async_get_data()` → platform entities render `coordinator.read_value(key)`. Writes route via `entity → coordinator.async_write → client.async_put_data`, with a 30s settle time (`_WRITE_SETTLE_TIME_S`) blocking re-reads to prevent stale device data from overwriting fresh writes.

## Known Dependencies
- **Internal**:
    - `pytherma` (vendored device library at `custom_components/xtherma_fp/pytherma/`; version `0.2.0`).
    - `modbus-connection` (`>=4.10.0,<5`; HA core pins `==4.10.0`, production backend tmodbus).
- **Deprecated**:
    - Vendored `pymodbus` under [`vendor/pymodbus/`](/workspaces/xtherma_ha/custom_components/xtherma_fp/vendor/pymodbus/) — dead since D4, deletion pending approval.
- **External**:
    - Home Assistant Core (`2026.9.x`).
    - `asyncio` (Standard Library).

## Testing Architecture

- **Framework**: `pytest` + `pytest-asyncio` on `pytest-homeassistant-custom-component`; snapshots via `syrupy` with `HomeAssistantSnapshotExtension`.
- **Layout** (`tests/`): `conftest.py` (fixtures), `helpers.py` (register injection + platform helpers), `const.py` (mock credentials), `fixtures/` (REST JSON payloads), `snapshots/` (syrupy `.ambr` baselines).
- **Transport mocking** (fully offline): REST via `aioclient_mock` (`mock_rest_api_client`); Modbus by patching the unit factory (`custom_components.xtherma_fp.async_get_unit`) with the library's in-memory `FakeUnit` (`mock_modbus_tcp_client`); integration lifecycles through `init_integration` / `init_modbus_integration`.
- **Test surface**: per platform (`sensor`, `binary_sensor`, `switch`, `number`, `select`), `config_flow`, coordinator/register mapping (`test_pytherma.py`), descriptor and translation consistency, common client logic.
- **Execution**: `python -m pytest --timeout=10`; regenerate baselines with `--snapshot-update` per affected test file; lint via `scripts/lint` (`ruff format` + `ruff check --fix`).
