# ToDo

## general roadmap

- [.] 1a - abstract classes and HEX protocol
- [.] 1b - CLI
- [ ] 2 - MQTT connector
- [ ] 3 - JSON protocol
- [ ] 4 - ext - Home Assistant

## phase 1 - HEX

- [x] protocol, message, payloads, primitive interpretation
- [x] sensor readings from all types of reports - container, decoding
- [ ] config - container, decoding RW, encoding W
- [ ] command - container, handle generic and reprovision (MQTT, WiFi), encoding W
- [ ] reasonable CLI to handle all of that

## phase 2 - MQTT

- [ ] connector to broker - R
- [ ] CLI for W

## phase 3 - JSON

same as HEX
