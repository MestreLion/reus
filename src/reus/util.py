# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
General utilities
"""
from __future__ import annotations

import argparse
import logging
import typing_extensions as t

if t.TYPE_CHECKING:
    import os

    PathLike: t.TypeAlias = t.Union[str, bytes, os.PathLike]

log: logging.Logger = logging.getLogger(__name__)


# For ArgumentParser.epilog
COPYRIGHT = """
Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""


class ReusError(Exception):
    """Base class for custom exceptions with %-formatting for args

    All modules in this package raise this (or a subclass) for all explicitly
    raised, business-logic, expected or handled exceptions.
    """

    def __init__(self, msg: object = "", *args: object):
        super().__init__((str(msg) % args) if args else msg)


def printf(msg: object = "", *args: object) -> None:
    """print() wrapper with %-formatting for args"""
    print((str(msg) % args) if args else msg)


def setup_logging(
    level: int = logging.INFO,
    fmt: str = "[%(asctime)s %(levelname)-6.6s] %(module)-4s: %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    style: t.Literal["%", "{", "$"] = "%",
) -> None:
    if level < logging.INFO:
        logging.basicConfig(level=level, format=fmt, datefmt=datefmt, style=style)
        return

    # Adapted from https://stackoverflow.com/a/25101727/624066
    class PlainInfo(logging.Formatter):
        info_formatter = logging.Formatter(style=style)

        def format(self, record: logging.LogRecord) -> str:
            if record.levelno == logging.INFO:
                return self.info_formatter.format(record)
            return super().format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(PlainInfo(fmt=fmt, datefmt=datefmt, style=style))
    logging.basicConfig(level=level, handlers=[handler])


class ArgumentParser(argparse.ArgumentParser):
    __doc__ = (
        (argparse.ArgumentParser.__doc__ or "")
        + """
    Changes:
    - description -- Only first non-blank line is considered, unless
        multiline is True.
    - epilog -- Default if None: <COPYRIGHT>. Set to empty string to disable.
        If set by the default or by a custom value, formatter_class used also
        changes to argparse.RawDescriptionHelpFormatter to respect line breaks.
    New Arguments:
    - multiline -- Do not limit description to its first non-blank line.
        (default: False)
    - loglevel_options -- dest (name) of pre-created logging level parser
        argument, set as mutually-exclusive -q/--quiet|-v/--verbose options.
        If empty, no such options are created. (default: "loglevel")
    - debug_option -- dest of the debug argument, a convenience bool
        attribute automatically created by parse_args() and set to True when
        the above loglevel is <logging.DEBUG> (i.e, when '-v|--verbose' is
        parsed). If empty, no such attribute is created. (default: "debug")
    - version
    Additions:
    FileType -- convenience class attribute, an alias to argparse.FileType
    Please note some caveats in argparse.FileType:
    - Opens immediately on parse_args(), and never closes the file.
        (but CPython does on scope exit, and you can use file in a context)
    - On Python < 3.9:
        - Modes "a" and "x" not allowed for path "-" (stdout in this case)
        - Does not work for stdin/stdout in binary mode (only affects Windows)
        - "-" uses plain stdin/stdout, which are buffered even in binary mode,
          and does not accept bytes, only str.
    - On Python >= 3.9, binary mode "-" uses stdin/stdout buffer directly,
        which might be missing if stdin/stdout were redirected to io.TextIO.
    See:
        https://github.com/python/cpython/issues/58032
        https://github.com/python/cpython/issues/58364
        https://docs.python.org/3/library/sys.html#sys.stdin
    """
    )
    FileType = argparse.FileType

    def __init__(
        self,
        *args: t.Any,
        multiline: bool = False,
        loglevel_options: str = "loglevel",
        debug_option: str = "debug",
        version: t.Optional[str] = None,
        **kwargs: t.Any,
    ):
        super().__init__(*args, **kwargs)

        if self.description is not None and not multiline:
            self.description = self.description.strip().split("\n", maxsplit=1)[0]

        if not self.epilog:
            if self.epilog is None:
                self.epilog = COPYRIGHT
                self.formatter_class = argparse.RawDescriptionHelpFormatter
            else:
                self.epilog = None

        self.loglevel_options = loglevel_options
        self.debug_option = debug_option

        if self.loglevel_options:
            group = self.add_mutually_exclusive_group()
            group.add_argument(
                "-q",
                "--quiet",
                dest=self.loglevel_options,
                const=logging.WARNING,
                default=logging.INFO,
                action="store_const",
                help="Suppress informative messages.",
            )
            group.add_argument(
                "-v",
                "--verbose",
                dest=self.loglevel_options,
                const=logging.DEBUG,
                action="store_const",
                help="Verbose mode, output extra info.",
            )

        if version:
            self.add_argument(
                "-V",
                "--version",
                action="version",
                version=f"%(prog)s {version}",
            )

    def parse_args(  # type: ignore  # accurate typing requires overload
        self, *args: t.Any, **kwargs: t.Any
    ) -> argparse.Namespace:
        __doc__ = argparse.ArgumentParser.parse_args.__doc__
        arguments: argparse.Namespace = super().parse_args(*args, **kwargs)
        if self.debug_option and self.loglevel_options:
            setattr(
                arguments,
                self.debug_option,
                getattr(arguments, self.loglevel_options) == logging.DEBUG,
            )
        return arguments
