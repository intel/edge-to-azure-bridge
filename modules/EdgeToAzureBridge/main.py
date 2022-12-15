# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""EII Message Bus Azure Edge Runtime Bridge
"""
import asyncio
import traceback as tb
import logging
from eab.bridge_state import BridgeState
from eab.mqtt_bridge import MQTTConnect


def main():
    """Main method.
    """
    log = logging.getLogger(__name__)
    bs = None
    connect = None
    try:
        bs = BridgeState.get_instance()
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except Exception as e:
        #print(f'[ERROR] {e}\n{tb.format_exc()}')
        log.error(f'[ERROR] Critical Error has occured in bridge module, ending connection')
        if bs is not None:
            # Fully stop the bridge
            bs.stop()
            loop.stop()
            loop.close()
        try:
            connect = MQTTConnect()
            connect.start()
        except Exception as e:
            if connect is not None:
                connect.stop()
            #print(f'[ERROR] {e}\n{tb.format_exc()}')
            log.error(f'[ERROR] Critical Error has occured in MQTT module, ending connection')

        raise

if __name__ == "__main__":
    main()
