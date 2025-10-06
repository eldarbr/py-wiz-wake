import logging
import time
import asyncio
from typing import Protocol
from effects import EffectCurve, LinearCapped
import datetime
from config import Config


class Light(Protocol):
    async def show_effect(self,
                          max_brightness: int,
                          start_ts: float,
                          end_ts: float,
                          curve: EffectCurve,
                          sampling_seconds: float = 10,
                          **pilot_kws) -> None:
        ...

    async def turn_off(self) -> None:
        ...


class Controller:
    def __init__(self, light: Light, conf: Config) -> None:
        self._light = light
        self._config = conf
        self._current_task: asyncio.Task | None = None

    async def _schedule_today(self) -> None:
        today_weekday = datetime.datetime.today().weekday()
        logging.info(f'_schedule_today start with the {today_weekday} day')

        if self._current_task is not None and not self._current_task.done():
            logging.info('_schedule_today kills previous routine')

            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass

        today_config = self._config.days[today_weekday]
        if today_config is None:
            logging.info(
                f'_schedule_today No alarm set up for the {today_weekday} day')
            return

        start_ts = datetime.datetime.combine(
            datetime.datetime.today(), today_config.start).timestamp()
        end_ts = datetime.datetime.combine(
            datetime.datetime.today(), today_config.end).timestamp()

        logging.info(
            f'_schedule_today setting effect starting at {start_ts}'
            f' and finishing at {end_ts}')

        effect_coro = self._light.show_effect(
            max_brightness=self._config.max_brightness,
            start_ts=start_ts,
            end_ts=end_ts,
            curve=LinearCapped(),
            colortemp=2200,
        )
        self._current_task = asyncio.create_task(effect_coro)

    async def control(self) -> None:
        await self._light.turn_off()

        while True:
            await self._schedule_today()

            tomorrow_now = \
                datetime.datetime.today() + datetime.timedelta(days=1)
            tomorrow_00_05 = datetime.datetime.combine(
                tomorrow_now.date(),
                datetime.time(hour=0, minute=5)
            )
            next_schedule_in = tomorrow_00_05.timestamp() - time.time()

            logging.info(
                f'control() sleeps, next schedule in {next_schedule_in},'
                f'{tomorrow_00_05.strftime("%d/%m/%Y, %H:%M:%S")}')

            await asyncio.sleep(next_schedule_in)
