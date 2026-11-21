# Topics: station s07

## Namespace
`bench/<station>/<thing>`

- `bench` is the shared root for the whole class bench.
- `<station>` is the station ID from `config.py` (mine is `s07`), so stations never collide.
- `<thing>` is what the message is about, in lowercase.

Subscribe to one station with `bench/s07/#`. Subscribe to one thing across all stations with `bench/+/light`.

## Topics

| Topic | Publisher | Subscriber | Payload | QoS | Retained |
|---|---|---|---|---|---|
| `bench/s07/light` | ESP32 node (`main.py`) | Pi (`lightmonitor.py`, `mosquitto_sub`) | Calibrated light level as plain text with one decimal, 0.0-100.0 (percent), e.g. `42.3` | 0 | No |

## Notes
- The payload is UTF-8 text, not JSON. The subscriber converts it with `float(msg.payload.decode())`.
- The node publishes once per second.
- QoS 0 because a lost reading is replaced by the next one a second later.
- Not retained because a stale light value would mislead a new subscriber.
- The client ID is `node-s07`. It must be unique per broker.
