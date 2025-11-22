# SPDX-FileCopyrightText: 2025-present Daniel Skowroński <daniel@skowron.ski>
#
# SPDX-License-Identifier: BSD-3-Clause

# IMPORTANT NOT ON ORIGIN OF PARTS OF COMMENTS/DOCS:
#   EVERYTHING PREFIXED WITH `SPEC:` AND BACK-TICK-QUOTED TEXT IS TAKEN ON 2025-11-22 DIRECTLY FROM 
#   [Qingping MQTT Protocol](https://developer.qingping.co/private/communication-protocols/public-mqtt-json)
#   WHICH IS OFFICIAL DOCUMENTATION PUBLISHED BY QINGPING. EVEN THEY ARE NOT 100% SURE.

from __future__ import annotations

# TODO: when using types from JsonFieldFormats, check if they contain method qp_json_encode for formatting and run it