# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Protocol as TypingProtocol
from enum import Enum, IntEnum, auto
from datetime import datetime

class SensorReadingType(Enum):
  REALTIME = auto()
  HISTORICAL = auto()
  EVENT = auto()
class ProtocolMessageDirection(Enum):
  DEVICE_TO_SERVER = auto()
  SERVER_TO_DEVICE = auto()
class ProtocolMessageCategory(Enum):
  READINGS = auto()
  SETTINGS = auto()
  REPROVISION = auto() # WiFi and MQTT change
  COMMAND = auto() # generic
  # TODO: implement others as needed

class SensorType(Enum):
  BATTERY = auto()
  TEMPERATURE = auto()
  TEMPERATURE_AUX = auto()
  PRESSURE = auto()
  HUMIDITY = auto()
  HUMIDITY_AUX = auto()
  PM1 = auto()
  PM25 = auto()
  PM10 = auto()
  CO2 = auto()
  CO2_CONC = auto()
  VOC = auto()
  NOISE = auto()
  LIGHT = auto()
  TVOC = auto()
  RADON = auto()
  SIGNAL_STRENGTH = auto()

class SensorReadingStatus(IntEnum):
  NORMAL = 0
  ABNORMAL = 1
  INITIALIZE = 2

@dataclass(frozen=True)
class SensorReading:
  """Single sensor reading data point."""
  sensor: SensorType
  value: float # FIXME: use Decimal?
  unit: str # either self-repoted or fixed per sensor type # TODO: this should be an Enum
  def __str__(self) -> str:
    return f"SensorReading(sensor={self.sensor.name}, value={self.value}, unit={self.unit})"


@dataclass(frozen=True)
class SensorReadingsContext:
  """Context for SensorReading.
  
  This is useful for readings that share common timestamp and origin, especially payloads that merge multiple readings.
  """
  origin: SensorReadingType
  timestamp: int
  readings: Iterable[SensorReading]
  status: SensorReadingStatus # TODO: verify this is for alerts
  level: Optional[int] = None
  status_duration: Optional[int] = None
  status_start_time: Optional[int] = None
  
  def __str__(self) -> str:
    return f"SensorReadingsContext(origin={self.origin.name}, timestamp={self.timestamp}, local_date='{datetime.fromtimestamp(self.timestamp)}' status={self.status.name}, readings_count={len(list(self.readings))})"
  
  def dump(self) -> str:
    msg = self.__str__()
    for reading in self.readings:
      msg += f"\n    - {reading}"
    return msg

class ProtocolMessage:
  """Abstract representation of message using Protocol."""
  
  direction: ProtocolMessageDirection
  """Metadata coming from lower layers.
  
  It is required, because some messages types are not safely inferable from message body alone.
  """
  
  category: ProtocolMessageCategory
  """Category of message, comparable to endpoint.
  
  Parts of converation should be in the same category, e.g. config request and response, sensor reading and ack, etc.
  """
  
  body: bytes
  """Unprocessed raw message transported using lower layer protocols.
  
  It can always be represented as bytes.
  """
  def __str__(self) -> str:
    return f"<{self.__class__.__name__} direction={self.direction.name} category={self.category.name} body_len={len(self.body)} bytes>"
  def dump(self) -> str:
    """Dump message content for debugging purposes."""
    return f"ProtocolMessage(direction={self.direction.name}, category={self.category.name}, body_len={len(self.body)} bytes>"


class SensorReadingsContainer():
  """Container for sensor reading reports, independent of protocol.
  
  There are 3 types of sensor readings, all carry list of timestamp to reading data entries:
  - real-time (initiated by device in intervals set by configuration),
    this message usually contains just one entry for latest reading data (of multiple sensors);
    however, documentation examples show multiple entries in single message as well (expected for retransmissions)
  - events/alerts (initiated by device when reading thresholds are outside limits set by configuration)
    nearly identical to real-time messages, but additionaly contain information on readings that triggered the event
    to abstract protocols, alert flag is carried in SensorReading.status field
  - historical (initiated by server when requesting past data stored on device)
    dynamic number of entries depending on how many readings were stored in requested period
  """
  readings: Iterable[SensorReadingsContext]
  category: ProtocolMessageCategory = field(
    default=ProtocolMessageCategory.READINGS
  )
  def __init__(self, message: ProtocolMessage):
    pass
  def dump(self) -> str:
    msg = f"SensorReadingsContainer(category={self.category.name}, readings_count={len(list(self.readings))})"
    for context in self.readings:
      msg += f"\n  - {context.dump()}"
    return msg
  # TODO: define common interfaces for getting SensorReading data from combined view - readings may contain duplicates
@dataclass(frozen=True)
class SettingsContainer():
  """Container for settings messages (read and writes), independent of protocol."""
  # TODO: implement this
@dataclass(frozen=True)
class CommandContainer():
  """Container for command messages (including reprovision), independent of protocol."""
  # TODO: implement this

class Protocol(TypingProtocol):
  """Abstract transport contract shared by JSON/HEX variants. This can be understood as Layer 4 in OSI model."""

  name: str
  version: str
  
  def decode_message(self, message: bytes, direction: ProtocolMessageDirection) -> ProtocolMessage:
    """Decode raw message bytes into a ProtocolMessage instance."""
    return ProtocolMessage()
  @classmethod
  def encode_message(cls, message: ProtocolMessage) -> bytes:
    """Encode a ProtocolMessage instance into raw message bytes."""
    return b""
