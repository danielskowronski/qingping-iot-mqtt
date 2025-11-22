# To-Do

## general roadmap

- [.] 1a - abstract classes and HEX protocol
- [.] 1b - CLI
- [.] 2 - MQTT connector and simple DB logging
- [ ] 3 - JSON protocol
- [ ] 4 - ext - Home Assistant

## phase 1 - HEX

- [x] protocol, message, payloads, primitive interpretation
- [x] sensor readings from all types of reports - container, decoding
- [.] config - container, decoding RW, encoding W
- [ ] command - container, handle generic and re-provision (MQTT, Wi-Fi), encoding W
- [ ] reasonable CLI to handle all of that

## phase 2 - MQTT and simple DB logging

- [x] connector to broker - R
- [x] SQLite connector and logging - storing events and raw
- [ ] SQLite connector - parsing replays
- [ ] CLI for W

## phase 3 - JSON

same as HEX
