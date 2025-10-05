from controller import Controller
from light import Light
import asyncio
import typing
import signal
import config
# import debugpy


CONFIG_PATH: typing.Final[str] = 'wake.conf'


async def main() -> None:
    conf = config.read_config(CONFIG_PATH)
    light = Light(mac=conf.bulb_mac, broadcast=conf.broadcast_addr)

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    try:
        await light.discover()
        controller = Controller(light, conf)

        control_task = asyncio.create_task(controller.control())

        await stop
        control_task.cancel()
        await asyncio.gather(control_task, return_exceptions=True)

    finally:
        print("Closing light connection...")
        await light.close()


if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5678))
    # debugpy.wait_for_client()

    asyncio.run(main())
