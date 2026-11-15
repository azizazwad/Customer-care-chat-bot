"""Windows integrations: approved apps, volume keys, and screen capture."""

from __future__ import annotations

import base64
import subprocess
import sys
from io import BytesIO

from .constants import APP_COMMANDS

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


def start_approved_app(name: str) -> bool:
    """Start an app from the approved list; return False if it is not on the list."""
    command = APP_COMMANDS.get(name.lower())
    if not command:
        return False
    subprocess.Popen(command, shell=False)
    return True


def volume_keys_available() -> bool:
    return sys.platform == "win32"


def press_volume_key(direction: int) -> None:
    """Press the Windows volume-up (direction > 0) or volume-down media key."""
    import ctypes
    key = 0xAF if direction > 0 else 0xAE  # VK_VOLUME_UP / VK_VOLUME_DOWN
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    ctypes.windll.user32.keybd_event(key, 0, 2, 0)


def screen_capture_available() -> bool:
    return ImageGrab is not None


def capture_screen_base64() -> str:
    """Capture the whole screen as a base64-encoded JPEG."""
    image = ImageGrab.grab().convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
