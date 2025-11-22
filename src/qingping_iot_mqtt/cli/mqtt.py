# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause
from qingping_iot_mqtt.config.schema import CliConfig, BrokerConfig, DeviceConfig
from qingping_iot_mqtt.protocols.base import ProtocolMessageDirection, ProtocolMessageCategory
from qingping_iot_mqtt.protocols.common_spec import ProtocolName
from qingping_iot_mqtt.protocols.hex import HexProtocol, HexSensorReadingMessage
from paho.mqtt import client as mqtt_client
from qingping_iot_mqtt.cli.db import log_sensor_reading, log_raw_payload
import json
import click

import logging
logger = logging.getLogger(__name__)

TRUNCATE_LENGTH = 128

prefixes_map: dict[str, str] = {}
direction_map: dict[str, ProtocolMessageDirection] = {}

def connect_mqtt(brokerConfig: BrokerConfig) -> mqtt_client.Client:
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      logger.info("Connected to MQTT Broker!")
    else:
      logger.error(f"Failed to connect, return code {rc}")
      raise click.ClickException("Failed to connect, return code.")

  client = mqtt_client.Client(
    client_id=brokerConfig.client_id,
    clean_session=brokerConfig.clean_session,
  )
  client.on_connect = on_connect
  client.username_pw_set(brokerConfig.username, brokerConfig.password)
  logger.debug(f"Connecting to MQTT broker at {brokerConfig.host}:{brokerConfig.port}...")
  client.connect(brokerConfig.host, brokerConfig.port, brokerConfig.keepalive)
  return client

def format_payload_logging(payload: bytes) -> str:
  length = len(payload)
  proto = ProtocolName.identify(payload)
  formatted = None
  if proto == ProtocolName.JSON:
    try:
      data = json.loads(payload)
      formatted = json.dumps(data, separators=(",", ":"))
    except json.JSONDecodeError:
      pass
  if formatted is None:
    truncated = str(payload[:TRUNCATE_LENGTH].hex().lower()) + ("..." if length > TRUNCATE_LENGTH else "")
    formatted = f"{length:4} bytes: {truncated}"

  return formatted

def subscribe(devices: list[DeviceConfig], client: mqtt_client.Client):
  def on_message(client, userdata, msg):
    logging.info(f"{prefixes_map.get(msg.topic, '!!')} {format_payload_logging(msg.payload)}")
    log_raw_payload(msg.topic, msg.payload)
    # TODO: handle some required server responses like JSON type 10 
    try:
      proto = ProtocolName.identify(msg.payload)
      if proto == ProtocolName.HEX:
        proto_msg = HexProtocol().decode_message(msg.payload, direction=direction_map.get(msg.topic, ProtocolMessageDirection.DEVICE_TO_SERVER))
        if proto_msg is not None and proto_msg.category == ProtocolMessageCategory.READINGS:
          readings_ctx = HexSensorReadingMessage(proto_msg)
          logging.debug(f"Decoded readings: {readings_ctx.dump()}")
          for rctx in readings_ctx.get_reading_contexts():
            log_sensor_reading(msg.topic, rctx)
    except Exception as e:
      logger.error(f"Error processing message on topic {msg.topic}: {e}")

  for device in devices:
    prefixes_map[device.topic_up] = f"{device.alias}>"
    direction_map[device.topic_up] = ProtocolMessageDirection.DEVICE_TO_SERVER
    client.subscribe(device.topic_up)
    prefixes_map[device.topic_down] = f"{device.alias}<"
    direction_map[device.topic_down] = ProtocolMessageDirection.SERVER_TO_DEVICE
    client.subscribe(device.topic_down)
  client.on_message = on_message

def run_mqtt_loop(config: CliConfig):
  client = connect_mqtt(config.broker)
  subscribe(config.devices, client)
  client.loop_forever()
