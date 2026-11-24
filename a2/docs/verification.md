# A2 verification table

| R-ID | Requirement | Check performed | Evidence | Status |
|------|-------------|-----------------|----------|--------|
| R-1 | Calibrated light loop & 0-100% clamping | Checked `read_pct()` and high/low error clamping | `mosquitto_sub` (`duty` at `100.0` and `0.0`) | pass |
| R-2 | Step response & disturbance recovery | Ran SP steps and shade/flashlight tests | `data/*.csv`, `mosquitto_sub` (`setpoint 50.0`) | pass |
| R-3 | MQTT telemetry | Subscribed to `bench/s07/#` | `mosquitto_sub` (`light`, `setpoint`, `duty`) | pass |