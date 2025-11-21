# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause
from qingping_iot_mqtt.config.schema import CliConfig, BrokerConfig, DeviceConfig
from qingping_iot_mqtt.protocols.base import ProtocolName
from paho.mqtt import client as mqtt_client
import json
import click
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

TRUNCATE_LENGTH = 128

prefixes_map: dict[str, str] = {}

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

  for device in devices:
    prefixes_map[device.topic_up] = f"{device.alias}<"
    client.subscribe(device.topic_up)
    prefixes_map[device.topic_up] = f"{device.alias}>"
    client.subscribe(device.topic_down)
  client.on_message = on_message

def run_mqtt_loop(config: CliConfig):
  client = connect_mqtt(config.broker)
  subscribe(config.devices, client)
  client.loop_forever()
