# python
import asyncio
import os

from dotenv import load_dotenv
from kasa import Discover
from kasa.exceptions import TimeoutError as KasaTimeoutError

load_dotenv()

IP_ADDRESS = os.getenv("KASA_DEVICE_IP")
USERNAME = os.getenv("KASA_USERNAME")
PASSWORD = os.getenv("KASA_PASSWORD")

outlets = {
    1: "heater",
    2: "lights",
    3: "mister",
    4: "basking_lamp",
}


async def _safe_close(dev):
    if dev is None:
        return
    for name in ("async_close", "close"):
        fn = getattr(dev, name, None)
        if fn:
            try:
                res = fn()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass
            return


async def toggle(powerstrip, outlet):
    target = powerstrip.children[outlet]
    print(f"Toggling {outlet} to {getattr(target, 'name', None)}")
    # get state
    current_state = getattr(target, "is_on", None)
    print(f"Current State: {current_state}")
    # toggle state
    if current_state:
        await target.turn_off()
        print(f"Turned off {getattr(target, 'name', None)}")
    else:
        await target.turn_on()
        print(f"Turned on {getattr(target, 'name', None)}")

    await powerstrip.update()


async def main():
    dev = None
    try:
        dev = await Discover.discover_single(IP_ADDRESS, username=USERNAME, password=PASSWORD)
        await dev.update()


        # example direct turn-on
        await dev.children[1].turn_on()
        await dev.update()
        print(f"Outlet 1 State: {dev.children[1].is_on}")

        # Fixed: await the coroutine
        await toggle(dev, 1)  # Example to toggle outlet1
    except KasaTimeoutError as e:
        print("Discovery timed out:", e)
    finally:
        await _safe_close(dev)


if __name__ == "__main__":
    asyncio.run(main())
