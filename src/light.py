import logging
import asyncio
from pywizlight import wizlight, discovery, PilotBuilder
from effects import EffectCurve
import time


class Light:
    def __init__(self, mac: str, broadcast: str) -> None:
        self._mac = mac
        self._broadcast = broadcast
        self._bulb: wizlight | None = None

    async def discover(self) -> None:
        bulbs = await discovery.discover_lights(
            broadcast_space=self._broadcast)

        for bulb in bulbs:
            if await bulb.getMac() == self._mac:
                self._bulb = bulb
                return

        raise ValueError("bulb not found")

    async def close(self) -> None:
        if self._bulb is None:
            raise ValueError("the bulb should be discovered first")
        await self._bulb.async_close()

    async def show_effect(self,
                          max_brightness: int,
                          start_ts: float,
                          end_ts: float,
                          curve: EffectCurve,
                          sampling_seconds: float = 15,
                          **pilot_kws) -> None:
        logging.info(
                f'show_effect() started for {time.ctime(start_ts)}')

        if self._bulb is None:
            raise ValueError("the bulb should be discovered first")

        if time.time() < start_ts:
            logging.info(
                f'show_effect() sleeps until {time.ctime(start_ts)} ({
                    start_ts - time.time()} secs)')
            await asyncio.sleep(start_ts - time.time())

            start_brightness = int(curve.get_value(0.0) * max_brightness)
            await self._bulb.turn_on(PilotBuilder(
                    brightness=start_brightness,
                    **pilot_kws))
            await asyncio.sleep(sampling_seconds)

        while time.time() < end_ts:
            curve_position = (time.time() - start_ts) / (end_ts - start_ts)
            current_brightness = \
                int(curve.get_value(curve_position) * max_brightness)
            await self._bulb.turn_on(PilotBuilder(
                brightness=current_brightness,
                **pilot_kws))
            await asyncio.sleep(sampling_seconds)

        end_brightness = int(curve.get_value(1.0) * max_brightness)
        await self._bulb.turn_on(PilotBuilder(
                brightness=end_brightness,
                **pilot_kws))

    async def turn_off(self) -> None:
        if self._bulb is None:
            raise ValueError("the bulb should be discovered first")

        await self._bulb.turn_off()
