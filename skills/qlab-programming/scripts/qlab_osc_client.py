"""
Reusable QLab OSC client/listener skeleton.

Use this as the starting point for "write me a Python script to control QLab"
requests instead of rebuilding the UDP/TCP plumbing each time. Fire-and-forget
commands (start/stop/pause/go) work fine over UDP. Anything that needs a
reply (property queries, isRunning polling) uses the TCP client, since QLab's
reply payloads can exceed a single UDP datagram and TCP round-trips are more
reliable for request/response.

Requires: pip install python-osc

Verify exact OSC address spellings against the live QLab docs for your
version before relying on this for a real show — see references/osc-dictionary.md
in this skill for the addressing conventions this script assumes.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from typing import Any

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_message


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 53000


class QLabUDPClient:
    """Fire-and-forget control over UDP. No replies."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._client = SimpleUDPClient(host, port)

    def send(self, address: str, *args: Any) -> None:
        self._client.send_message(address, list(args))

    # --- convenience wrappers for the most common global commands ---
    def go(self) -> None:
        self.send("/go")

    def stop(self) -> None:
        self.send("/stop")

    def panic(self) -> None:
        self.send("/panic")

    def start_cue(self, cue_number: str) -> None:
        self.send(f"/cue/{cue_number}/start")

    def stop_cue(self, cue_number: str) -> None:
        self.send(f"/cue/{cue_number}/stop")

    def load_cue(self, cue_number: str) -> None:
        self.send(f"/cue/{cue_number}/load")

    def start_cue_by_id(self, cue_id: str) -> None:
        self.send(f"/cue_id/{cue_id}/start")


class QLabTCPClient:
    """
    Request/response over TCP. QLab wraps OSC packets with a 4-byte
    big-endian length prefix on TCP (standard OSC-over-TCP framing) —
    this client handles that framing for you.
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 5.0):
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._timeout = timeout

    def close(self) -> None:
        self._sock.close()

    def _send_packet(self, address: str, args: list[Any]) -> None:
        builder = OscMessageBuilder(address=address)
        for a in args:
            builder.add_arg(a)
        msg = builder.build()
        payload = msg.dgram
        length_prefix = len(payload).to_bytes(4, "big")
        self._sock.sendall(length_prefix + payload)

    def _recv_packet(self) -> osc_message.OscMessage:
        length_bytes = self._recv_exact(4)
        length = int.from_bytes(length_bytes, "big")
        payload = self._recv_exact(length)
        return osc_message.OscMessage(payload)

    def _recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("QLab closed the TCP connection")
            buf += chunk
        return buf

    def query(self, address: str, *args: Any) -> dict:
        """
        Send an OSC message expecting a reply on /reply/<address>, and
        return the parsed JSON body QLab sends as the reply's first argument.
        """
        self._send_packet(address, list(args))
        reply = self._recv_packet()
        # QLab's reply argument is a JSON string: {"status": "ok", "address": ..., "data": ...}
        raw = reply.params[0] if reply.params else "{}"
        return json.loads(raw)

    def connect_workspace(self, workspace_id: str, passcode: str) -> dict:
        """Authenticate against a passcode-protected workspace before other
        commands will be accepted. No-op (but harmless) if no passcode is set."""
        return self.query(f"/workspace/{workspace_id}/connect", passcode)

    def wait_for_cue_to_finish(self, cue_number: str, poll_interval: float = 0.25, timeout: float | None = None) -> None:
        """Poll /cue/{number}/isRunning until it goes false. Simple and
        portable; see references/osc-dictionary.md for the alternative
        push-based approach using OSC status updates if latency matters."""
        start = time.monotonic()
        while True:
            result = self.query(f"/cue/{cue_number}/isRunning")
            if result.get("data") is False:
                return
            if timeout is not None and (time.monotonic() - start) > timeout:
                raise TimeoutError(f"Cue {cue_number} did not finish within {timeout}s")
            time.sleep(poll_interval)


if __name__ == "__main__":
    # Example: fire cue 12 and wait for it to finish, then fire cue 13.
    udp = QLabUDPClient()
    tcp = QLabTCPClient()

    udp.start_cue("12")
    tcp.wait_for_cue_to_finish("12", timeout=60)
    udp.start_cue("13")

    tcp.close()
