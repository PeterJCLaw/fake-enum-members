from __future__ import annotations

import contextlib
import enum
import unittest
from typing import Iterator, Type
from unittest import mock


class Times(enum.Enum):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    EVENING = 'evening'


@contextlib.contextmanager
def mock_extend_enum(
    enum_class: Type[enum.Enum],
    **kwargs: object,
) -> Iterator[None]:
    members = enum._EnumDict()  # type: ignore[attr-defined]
    for name, value in kwargs.items():
        members[name] = value

    # Use the underlying enum for construction so that we get as close as
    # possible to "real" members. However this means we need to convince the
    # enum machinery the underlying class doesn't have any members (since
    # extension of enums is normally not allowed).
    with mock.patch.object(enum_class, '_member_names_', new=[]):
        extended_enum_class: Type[enum.Enum] = type(
            f'Test{enum_class.__name__}',
            (enum_class,),
            members,
        )

    by_name = {x: extended_enum_class[x] for x in kwargs.keys()}
    by_value = {y: extended_enum_class[x] for x, y in kwargs.items()}

    with mock.patch.dict(
        enum_class._member_map_,
        by_name,
    ), mock.patch.dict(
        enum_class._value2member_map_,
        by_value,
    ):
        yield


class Test(unittest.TestCase):
    def test_times_initial(self) -> None:
        with self.subTest('known attribute'):
            Times.MORNING

        with self.subTest('known lookup'):
            Times['MORNING']

        with self.subTest('known construct'):
            Times('morning')

        with self.subTest('unknown member'):
            with self.assertRaises(AttributeError):
                Times.EARLY_MORNING  # type: ignore[attr-defined]

        with self.subTest('unknown lookup'):
            with self.assertRaises(KeyError):
                Times['EARLY_MORNING']

        with self.subTest('unknown construct'):
            with self.assertRaises(ValueError):
                Times('early_morning')

    def test_times_mocked(self) -> None:
        with mock_extend_enum(Times, EARLY_MORNING='early_morning'):
            with self.subTest('existing attribute'):
                Times.MORNING

            with self.subTest('existing lookup'):
                Times['MORNING']

            with self.subTest('existing construct'):
                Times('morning')

            with self.subTest('new member'):
                Times.EARLY_MORNING  # type: ignore[attr-defined]

            with self.subTest('new lookup'):
                Times['EARLY_MORNING']

            with self.subTest('new construct'):
                Times('early_morning')


if __name__ == '__main__':
    unittest.main()
