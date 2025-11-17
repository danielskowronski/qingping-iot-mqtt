# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause
import click

from qingping_iot_mqtt.__about__ import __version__
from qingping_iot_mqtt.protocols.base import ProtocolMessageDirection
from qingping_iot_mqtt.protocols.hex import HexProtocol, ProtocolMessageCategory, HexSensorReadingMessage


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="qingping-iot-mqtt")
def qingping_iot_mqtt():
  pass


@qingping_iot_mqtt.group("manual")
def manual_group():
  """Manual protocol helpers."""


@manual_group.command("hex")
@click.option("--incoming", "incoming_hex", required=True, help="Raw HEX frame as hex string (spaces allowed).")
def manual_hex(incoming_hex: str):
  """Decode HEX protocol message assuming it was sent by a device."""
  cleaned = "".join(ch for ch in incoming_hex if not ch.isspace())
  if len(cleaned) % 2 != 0:
    raise click.BadParameter("HEX payload must consist of full bytes (even number of hex digits).")
  try:
    raw = bytes.fromhex(cleaned)
  except ValueError as exc:
    raise click.BadParameter(f"Invalid HEX payload: {exc}") from exc

  if raw[0:2] == b'\x7b\x0a':
    click.echo("Detected JSON protocol frame. Use appropriate tool to decode JSON frames.")
    return

  protocol = HexProtocol()
  message = protocol.decode_message(raw, ProtocolMessageDirection.DEVICE_TO_SERVER)
  click.echo(message.dump())
  if message.category== ProtocolMessageCategory.READINGS:
    click.echo(HexSensorReadingMessage(message).dump())
