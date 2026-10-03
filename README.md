<h2 align="center">
   <a href="https://www.xtherma.de/">Xtherma</a> Heatpump integration for <a href="https://www.home-assistant.io">Home Assistant</a>
   </br></br>
</h2>

Home Assistant integration for Xtherma heatpumps. It supports two interchangeable
connection types, selected per config entry:

| | Fernportal REST API | Modbus/TCP |
|---|---|---|
| Path | cloud (`fernportal.xtherma.de`) | local network |
| Access | read-only | read + write |
| Polling | 1 min (server rate limit) | 30 s |
| Entities | ~88 | ~92 |

## Features

- **Sensors** — temperatures (flow/return/hot water/tank), heating power,
  power consumption, energy counters, and more.
- **Binary sensors** — pumps, system faults, EVU and §14a EnWG lock states.
- **Switches / numbers / selects** (writable via Modbus/TCP) — operating mode,
  setpoints, heating/cooling curves, SG-ready settings, and more. When paired
  over the REST API these entities exist but are read-only; attempting to
  change them reports a "read-only" error instead of writing.
- Automatic device registry entry, reconfigure flow, and English/German UI.

## Requirements

- Home Assistant `2026.9.0` or newer (the core **Modbus** integration is used
  as the Modbus/TCP transport and is loaded automatically).
- For the REST variant: a Fernportal account (serial number + API token).
- For the Modbus/TCP variant: the heatpump reachable via Modbus/TCP on your
  LAN (host, port, slave address).

## Installation (HACS)

1. Go to your Home Assistant > HACS management page.
2. Open the three-dot menu and select `Custom repositories`.
3. In the repository field, add `https://github.com/Xtherma-Warmepumpen/xtherma_ha` and select type `Integration`.
4. Click `Add`.

After that, you can search and download the Xtherma integration. Once downloaded within HACS, you will be able to add it via Home Assistant's **Settings > Devices & Services > Add Integration**.

## Installation (manual)

Copy the folder `custom_components/xtherma_fp` into the HA installation so that it can be found under `/config/custom_components/xtherma_fp`.
Then restart Home Assistant.

## Configuration

In **Settings > Devices & Services**, click on **Add Integration** and search for **Xtherma**. The flow asks for:

1. **Name** of the entry and the **serial number** of the Fernportal module (format `FP-XX-XXXXXX`).
2. **Connection type** — pick one:
   - **Fernportal REST API (cloud)**: your **API token**. Both the token and the serial number can be copied from the remote portal (Start page -> My Account).
   - **Modbus/TCP (local)**: **IP address** (default port `502`, slave address `1`).

The settings are validated against the device before the entry is created.
Use **Configure** on the finished entry to switch connection type or change
credentials later (reconfigure flow).

### Options

- **Detect empty data on Modbus/TCP** (on by default): ignores empty readings
  from the Modbus/TCP server to avoid jumps in sensor history.

## Troubleshooting & Logging

The most common setup errors are reported directly in the config flow
(e.g. wrong API token, Fernportal rate limit, unreachable Modbus server).

Debug logs can be enabled as follows:

```yaml
logger:
  default: info
  logs:
    custom_components.xtherma_fp: debug
```

## Good to know

- **REST API**: the Fernportal server is rate limited to roughly one request
  per minute; the integration stays within that limit automatically. If you
  just set up the integration, expect the first values to appear within a
  minute.
- **Modbus/TCP**: values are refreshed every 30 seconds. After changing a
  setting, the integration briefly blocks re-reads so that fresh writes are
  not overwritten by stale device data.
- Write access (switches, numbers, selects) requires the Modbus/TCP
  connection; over REST these entities are display-only.
- Some registers are read-only on the device itself, independent of
  connection type; attempts to change them are rejected with an error.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

Issues: <https://github.com/Xtherma-Warmepumpen/xtherma_ha/issues>
