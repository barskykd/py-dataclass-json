import datetime
import unittest
from dataclasses import dataclass
from enum import Enum
from typing import Dict, NamedTuple, List, Union

import dataclass_json
from dataclass_json import UNDEFINED


class WindDirection(Enum):
    North = "N"
    South = "S"
    West = "W"
    East = "E"


class Precipitation(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime


@dataclass
class Extra1:
    int_field: int
    str_field: str


@dataclass
class WeatherData:
    temperatures: Dict[datetime.datetime, float]
    wind_direction: WindDirection
    precipitations: List[Precipitation]
    just_dict: Dict = None


class DataClassJsonTests(unittest.TestCase):
    def test_to_dict(self):
        wd = WeatherData(
            temperatures={
                datetime.datetime(2022, 12, 28, 17, 48, 0): 22.2,
                datetime.datetime(2022, 12, 28, 17, 48, 1): 25.2
            },
            wind_direction=WindDirection.North,
            precipitations=[
                Precipitation(datetime.datetime(2022, 12, 28, 10, 48, 0), datetime.datetime(2022, 12, 28, 12, 48, 0)),
                Precipitation(datetime.datetime(2022, 12, 28, 14, 48, 0), datetime.datetime(2022, 12, 28, 16, 48, 0))
            ],
            just_dict={}
        )

        wd_dict = dataclass_json.to_dict(wd)

        self.assertDictEqual(wd_dict, {'precipitations': [{'end': '2022-12-28T12:48:00',
                                                           'start': '2022-12-28T10:48:00'},
                                                          {'end': '2022-12-28T16:48:00',
                                                           'start': '2022-12-28T14:48:00'}],
                                       'temperatures': {'2022-12-28T17:48:00': 22.2, '2022-12-28T17:48:01': 25.2},
                                       'wind_direction': 'N',
                                       'just_dict': {}
                                       }
                             )

    def test_to_list(self):
        wd = WeatherData(
            temperatures={
                datetime.datetime(2022, 12, 28, 17, 48, 0): 22.2,
                datetime.datetime(2022, 12, 28, 17, 48, 1): 25.2
            },
            wind_direction=WindDirection.North,
            precipitations=[
                Precipitation(datetime.datetime(2022, 12, 28, 10, 48, 0),
                              datetime.datetime(2022, 12, 28, 12, 48, 0)),
                Precipitation(datetime.datetime(2022, 12, 28, 14, 48, 0),
                              datetime.datetime(2022, 12, 28, 16, 48, 0))
            ]
        )

        wd_list = dataclass_json.to_list([wd])

        self.assertEqual(wd_list, [{'precipitations': [{'end': '2022-12-28T12:48:00',
                                                        'start': '2022-12-28T10:48:00'},
                                                       {'end': '2022-12-28T16:48:00',
                                                        'start': '2022-12-28T14:48:00'}],
                                    'temperatures': {'2022-12-28T17:48:00': 22.2, '2022-12-28T17:48:01': 25.2},
                                    'wind_direction': 'N',
                                    'just_dict': None
                                    }
                                   ])

    def test_from_dict(self):
        wd_dict = {'precipitations': [{'end': '2022-12-28T12:48:00',
                                       'start': '2022-12-28T10:48:00'},
                                      {'end': '2022-12-28T16:48:00',
                                       'start': '2022-12-28T14:48:00'}],
                   'temperatures': {'2022-12-28T17:48:00': 22.2, '2022-12-28T17:48:01': 25.2},
                   'wind_direction': 'N'
                   }

        wd = dataclass_json.from_dict(WeatherData, wd_dict)

        self.assertEqual(wd, WeatherData(temperatures={datetime.datetime(2022, 12, 28, 17, 48): 22.2,
                                                       datetime.datetime(2022, 12, 28, 17, 48, 1): 25.2},
                                         wind_direction=WindDirection.North,
                                         precipitations=[
                                             Precipitation(start=datetime.datetime(2022, 12, 28, 10, 48),
                                                           end=datetime.datetime(2022, 12, 28, 12, 48)),
                                             Precipitation(start=datetime.datetime(2022, 12, 28, 14, 48),
                                                           end=datetime.datetime(2022, 12, 28, 16, 48))]))

    def test_from_list(self):
        wd_list = [{'precipitations': [{'end': '2022-12-28T12:48:00',
                                        'start': '2022-12-28T10:48:00'},
                                       {'end': '2022-12-28T16:48:00',
                                        'start': '2022-12-28T14:48:00'}],
                    'temperatures': {'2022-12-28T17:48:00': 22.2, '2022-12-28T17:48:01': 25.2},
                    'wind_direction': 'N'
                    }]

        wd = dataclass_json.from_list(WeatherData, wd_list)

        self.assertEqual(wd, [WeatherData(temperatures={datetime.datetime(2022, 12, 28, 17, 48): 22.2,
                                                        datetime.datetime(2022, 12, 28, 17, 48, 1): 25.2},
                                          wind_direction=WindDirection.North,
                                          precipitations=[
                                              Precipitation(start=datetime.datetime(2022, 12, 28, 10, 48),
                                                            end=datetime.datetime(2022, 12, 28, 12, 48)),
                                              Precipitation(start=datetime.datetime(2022, 12, 28, 14, 48),
                                                            end=datetime.datetime(2022, 12, 28, 16, 48))],
                                          )])

        if __name__ == '__main__':
            unittest.main()

    def test_union(self):
        dataclass_json.from_list(Union[Extra1, Precipitation], [{'end': None, 'start': None},
                                                                {'int_field': 10, 'str_field': '20'}])

    def test_missing(self):
        @dataclass
        class Foo:
            field1: int = UNDEFINED
            field2: str = UNDEFINED
            field3: bool = UNDEFINED

        dict = dataclass_json.to_dict(Foo(field3=False))
        self.assertDictEqual(dict, {"field3": False})
