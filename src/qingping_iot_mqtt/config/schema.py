# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause
import platform
from typing import Optional
from pydantic import BaseModel
from qingping_iot_mqtt.protocols.base import ProtocolName

class BrokerConfig(BaseModel):
  host: str
  port: int
  username: str
  password: str
  client_id: str = platform.node()
  keepalive: int = 60
  clean_session: bool = True
class DeviceConfig(BaseModel):
  alias: str
  mac: str
  topic_up: str
  topic_down: str
  protocol: ProtocolName
  model: str # FIXME, should be Enum or better class to handle models and capabilities

class CliConfig(BaseModel):
  broker: BrokerConfig
  devices: list[DeviceConfig]
