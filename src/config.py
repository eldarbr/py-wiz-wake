import datetime
import typing
import yaml
from dataclasses import dataclass, field


@dataclass
class Config:
    @dataclass
    class DayInfo:
        start: datetime.time
        end: datetime.time

    max_brightness: int
    broadcast_addr: str
    bulb_mac: str
    days: list[DayInfo | None] = field(default_factory=lambda: [None] * 7)


def read_config(path: str) -> Config:
    weekdays: typing.Final[list[str]] \
        = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    data: typing.Any

    with open(path, "r") as conf_f:
        try:
            data = yaml.safe_load(conf_f)
        except yaml.YAMLError as exc:
            raise ValueError("error in configuration file:", exc)

    if "max_brightness" not in data or \
       int(data["max_brightness"]) < 0 or int(data["max_brightness"]) > 255:
        raise ValueError("error in configuration file:"
                         "max_brightness should be a part of the config"
                         "and should be in the range [0, 255]")

    if 'days' not in data:
        raise ValueError("error in configuration file:"
                         "days should be a part of the config")

    days: list[Config.DayInfo | None] = [None] * 7

    for i, day_name in enumerate(weekdays):
        if day_name not in data['days']:
            continue

        day_conf_data = data['days'][day_name]
        if "end" not in day_conf_data or "start" not in day_conf_data:
            raise ValueError("error in configuration file:"
                             "start and end should be part of each day")

        day_conf = Config.DayInfo(
            end=datetime.datetime.strptime(
                day_conf_data["end"], "%H:%M").time(),
            start=datetime.datetime.strptime(
                day_conf_data["start"], "%H:%M").time()
        )

        days[i] = day_conf

    if 'bulb_mac' not in data:
        raise ValueError("error in configuration file:"
                         "bulb_mac should be a part of the config")

    if 'broadcast_addr' not in data:
        raise ValueError("error in configuration file:"
                         "broadcast_addr should be a part of the config")

    return Config(
        max_brightness=int(data["max_brightness"]),
        broadcast_addr=data['broadcast_addr'],
        bulb_mac=data['bulb_mac'],
        days=days
    )
