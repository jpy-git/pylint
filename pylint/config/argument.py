# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

"""Definition of an Argument class and transformers for various argument types.

An Argument instance represents a pylint option to be handled by an argparse.ArgumentParser
"""


import argparse
import pathlib
import re
from typing import Callable, Dict, List, Optional, Pattern, Sequence, Tuple, Union

from pylint import interfaces
from pylint import utils as pylint_utils

_ArgumentTypes = Union[
    str,
    int,
    float,
    bool,
    Pattern[str],
    Sequence[str],
    Sequence[Pattern[str]],
    Tuple[int, ...],
]
"""List of possible argument types."""


def _confidence_transformer(value: str) -> Sequence[str]:
    """Transforms a comma separated string of confidence values."""
    values = pylint_utils._check_csv(value)
    for confidence in values:
        if confidence not in interfaces.CONFIDENCE_LEVEL_NAMES:
            raise argparse.ArgumentTypeError(
                f"{value} should be in {*interfaces.CONFIDENCE_LEVEL_NAMES,}"
            )
    return values


def _csv_transformer(value: str) -> Sequence[str]:
    """Transforms a comma separated string."""
    return pylint_utils._check_csv(value)


YES_VALUES = {"y", "yes", "true"}
NO_VALUES = {"n", "no", "false"}


def _yn_transformer(value: str) -> bool:
    """Transforms a yes/no or stringified bool into a bool."""
    value = value.lower()
    if value in YES_VALUES:
        return True
    if value in NO_VALUES:
        return False
    raise argparse.ArgumentTypeError(
        None, f"Invalid yn value '{value}', should be in {*YES_VALUES, *NO_VALUES}"
    )


def _non_empty_string_transformer(value: str) -> str:
    """Check that a string is not empty and remove quotes."""
    if not value:
        raise argparse.ArgumentTypeError("Option cannot be an empty string.")
    return pylint_utils._unquote(value)


def _py_version_transformer(value: str) -> Tuple[int, ...]:
    """Transforms a version string into a version tuple."""
    try:
        version = tuple(int(val) for val in value.split("."))
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} has an invalid format, should be a version string. E.g., '3.8'"
        ) from None
    return version


def _regexp_csv_transfomer(value: str) -> Sequence[Pattern[str]]:
    """Transforms a comma separated list of regular expressions."""
    patterns: List[Pattern[str]] = []
    for pattern in _csv_transformer(value):
        patterns.append(re.compile(pattern))
    return patterns


def _regexp_paths_csv_transfomer(value: str) -> Sequence[Pattern[str]]:
    """Transforms a comma separated list of regular expressions paths."""
    patterns: List[Pattern[str]] = []
    for pattern in _csv_transformer(value):
        patterns.append(
            re.compile(
                str(pathlib.PureWindowsPath(pattern)).replace("\\", "\\\\")
                + "|"
                + pathlib.PureWindowsPath(pattern).as_posix()
            )
        )
    return patterns


_TYPE_TRANSFORMERS: Dict[str, Callable[[str], _ArgumentTypes]] = {
    "choice": str,
    "csv": _csv_transformer,
    "float": float,
    "int": int,
    "confidence": _confidence_transformer,
    "non_empty_string": _non_empty_string_transformer,
    "py_version": _py_version_transformer,
    "regexp": re.compile,
    "regexp_csv": _regexp_csv_transfomer,
    "regexp_paths_csv": _regexp_paths_csv_transfomer,
    "string": pylint_utils._unquote,
    "yn": _yn_transformer,
}
"""Type transformers for all argument types.

A transformer should accept a string and return one of the supported
Argument types. It will only be called when parsing 1) command-line,
2) configuration files and 3) a string default value.
Non-string default values are assumed to be of the correct type.
"""


class _Argument:
    """Class representing an argument to be passed by an argparse.ArgumentsParser.

    This is based on the parameters passed to argparse.ArgumentsParser.add_message.
    See:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument
    """

    def __init__(
        self,
        flags: List[str],
        action: str,
        default: _ArgumentTypes,
        arg_type: str,
        choices: Optional[List[str]],
        arg_help: str,
        metavar: str,
    ) -> None:
        self.flags = flags
        """The name of the argument."""

        self.action = action
        """The action to perform with the argument."""

        self.type = _TYPE_TRANSFORMERS[arg_type]
        """A transformer function that returns a transformed type of the argument."""

        self.default = default
        """The default value of the argument."""

        self.choices = choices
        """A list of possible choices for the argument.

        None if there are no restrictions.
        """

        # argparse uses % formatting on help strings, so a % needs to be escaped
        self.help = arg_help.replace("%", "%%")
        """The description of the argument."""

        self.metavar = metavar
        """The metavar of the argument.

        See:
        https://docs.python.org/3/library/argparse.html#metavar
        """


class _StoreTrueArgument:
    """Class representing a 'store_true' argument to be passed by an argparse.ArgumentsParser.

    This is based on the parameters passed to argparse.ArgumentsParser.add_message.
    See:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument
    """

    def __init__(
        self,
        flags: List[str],
        action: str,
        default: _ArgumentTypes,
        arg_help: str,
    ) -> None:
        self.flags = flags
        """The name of the argument."""

        self.action = action
        """The action to perform with the argument."""

        self.default = default
        """The default value of the argument."""

        # argparse uses % formatting on help strings, so a % needs to be escaped
        self.help = arg_help.replace("%", "%%")
        """The description of the argument."""
