import asyncio
import os
import logging
from typing import Optional

from dotenv import load_dotenv

try:
    from kasa import Discover
    from kasa.exceptions import TimeoutError as KasaTimeoutError
    KASA_AVAILABLE = True
except ImportError:
    KASA_AVAILABLE = False
    logging.warning("kasa module not available - powerstrip functionality disabled")

load_dotenv()

logger = logging.getLogger("powerstrip")

IP_ADDRESS = os.getenv("KASA_DEVICE_IP")
USERNAME = os.getenv("KASA_USERNAME")
PASSWORD = os.getenv("KASA_PASSWORD")


class PowerstripUnavailableError(Exception):
    """Raised when the kasa powerstrip cannot be contacted or discovered."""


async def _call_and_await(fn, *args, **kwargs):
    """Call a function which may return a coroutine; await if needed."""
    res = fn(*args, **kwargs)
    if asyncio.iscoroutine(res):
        return await res
    return res


async def _safe_update(obj):
    if obj is None:
        return
    upd = getattr(obj, "update", None)
    if callable(upd):
        try:
            await _call_and_await(upd)
        except Exception:
            logger.debug("_safe_update failed", exc_info=True)


async def _safe_close(dev):
    if dev is None:
        return
    for name in ("async_close", "close"):
        fn = getattr(dev, name, None)
        if fn:
            try:
                await _call_and_await(fn)
            except Exception:
                logger.debug("_safe_close failed", exc_info=True)
            return


async def _get_device() -> object:
    """Discover and return a kasa device instance.

    Prefers KASA_DEVICE_IP if set; otherwise picks the first discovered device.
    Raises PowerstripUnavailableError when discovery times out or no devices are found.
    Other unexpected exceptions are allowed to bubble up.
    """
    if not KASA_AVAILABLE:
        raise PowerstripUnavailableError("kasa module not available")

    try:
        if IP_ADDRESS:
            return await Discover.discover_single(IP_ADDRESS, username=USERNAME, password=PASSWORD)
        devices = await Discover.discover()
        if not devices:
            logger.warning("No Kasa devices found on the network")
            raise PowerstripUnavailableError("No Kasa devices found on the network")
        _, dev = next(iter(devices.items()))
        return dev
    except KasaTimeoutError as e:
        logger.warning("Kasa discovery timed out", exc_info=True)
        raise PowerstripUnavailableError("Kasa discovery timed out") from e


async def get_outlet_state(index: int) -> Optional[bool]:
    """Return True/False for outlet state, or None if unknown.
    Index is 1-based (to match existing project usage).
    """
    dev = None
    try:
        dev = await _get_device()
        await _safe_update(dev)
        zero_idx = index - 1
        # prefer children/relays
        relays = getattr(dev, "relays", None) or getattr(dev, "children", None)
        if relays and 0 <= zero_idx < len(relays):
            item = relays[zero_idx]
            await _safe_update(item)
            return getattr(item, "is_on", None)
        # modules mapping
        modules = getattr(dev, "modules", None)
        if modules:
            items = list(modules.items())
            if 0 <= zero_idx < len(items):
                _, module = items[zero_idx]
                await _safe_update(module)
                return getattr(module, "is_on", None)
        # fallback to device-level is_on
        return getattr(dev, "is_on", None)
    finally:
        await _safe_close(dev)


async def set_outlet_state(index: int, action: str) -> Optional[bool]:
    """Set the outlet to 'on', 'off', or 'toggle'. Returns resulting state or None.

    Index is 1-based.
    """
    action = action.lower()
    if action not in ("on", "off", "toggle"):
        raise ValueError("action must be 'on', 'off' or 'toggle'")

    dev = None
    try:
        dev = await _get_device()
        await _safe_update(dev)
        zero_idx = index - 1

        relays = getattr(dev, "relays", None) or getattr(dev, "children", None)
        if relays and 0 <= zero_idx < len(relays):
            item = relays[zero_idx]
            await _safe_update(item)
            # determine desired action
            if action == "toggle":
                current = getattr(item, "is_on", False)
                action = "off" if current else "on"
            fn = getattr(item, "turn_on" if action == "on" else "turn_off", None) or getattr(item, f"async_turn_{'on' if action=='on' else 'off'}", None)
            if fn is None:
                # try device-level API
                dev_fn = getattr(dev, "turn_on" if action == "on" else "turn_off", None)
                if dev_fn:
                    try:
                        await _call_and_await(dev_fn, zero_idx)
                    except TypeError:
                        await _call_and_await(dev_fn)
                else:
                    raise RuntimeError("No method to control outlet")
            else:
                await _call_and_await(fn)
            await _safe_update(item)
            return getattr(item, "is_on", None)

        # modules mapping
        modules = getattr(dev, "modules", None)
        if modules:
            items = list(modules.items())
            if 0 <= zero_idx < len(items):
                _, module = items[zero_idx]
                await _safe_update(module)
                if action == "toggle":
                    current = getattr(module, "is_on", False)
                    action = "off" if current else "on"
                fn = getattr(module, "turn_on" if action == "on" else "turn_off", None) or getattr(module, f"async_turn_{'on' if action=='on' else 'off'}", None)
                if fn:
                    await _call_and_await(fn)
                    await _safe_update(module)
                    return getattr(module, "is_on", None)

        # device-level fallback
        if action == "toggle":
            # best-effort: toggle based on device state
            current = getattr(dev, "is_on", None)
            if current is None:
                raise RuntimeError("Cannot determine device state to toggle")
            action = "off" if current else "on"
        dev_fn = getattr(dev, "turn_on" if action == "on" else "turn_off", None) or getattr(dev, f"async_turn_{'on' if action=='on' else 'off'}", None)
        if dev_fn:
            try:
                await _call_and_await(dev_fn, zero_idx)
            except TypeError:
                await _call_and_await(dev_fn)
            await _safe_update(dev)
            relays = getattr(dev, "relays", None) or getattr(dev, "children", None)
            if relays and 0 <= zero_idx < len(relays):
                return getattr(relays[zero_idx], "is_on", None)
            return getattr(dev, "is_on", None)

        raise RuntimeError("No suitable method to control outlet on this device")
    finally:
        await _safe_close(dev)


async def initialize():
    """Initialize the powerstrip interface. Currently a no-op but allows graceful startup."""
    logger.info("Powerstrip interface initialized")


async def cleanup():
    """Cleanup powerstrip interface on shutdown."""
    logger.info("Powerstrip interface cleanup")
