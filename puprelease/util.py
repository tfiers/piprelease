from dataclasses import dataclass
from re import sub
from subprocess import check_output
from textwrap import fill
from typing import Optional, Sequence
from warnings import warn

import click


MAX_LINEWIDTH = 75


@dataclass
class ExitSignal(Exception):
    message: Optional[str] = None


def echo(
    message: str = "",
    newline: bool = True,
    raw: bool = False,
    max_linewidth: int = MAX_LINEWIDTH,
):
    if not raw:
        message = rewrap(message, width=max_linewidth)
    click.echo(message, nl=newline)


def get_stripped_output(cmd: Sequence[str]) -> str:
    output: bytes = check_output(cmd)
    return output.decode().strip()


def print_own_version():
    # fmt: off
    try:
        import puprelease
        version = puprelease.__version__
    except ModuleNotFoundError:
        # puprelease is not installed; Running as a script
        import setuptools_scm
        version = setuptools_scm.get_version(root="..", relative_to=__file__)
    echo(f"This is puprelease version {version}")
    # fmt: on


def print_header(header: str):
    """ Underline the given string and prefix with a blank line. """
    echo()
    echo(header)
    echo("-" * len(header))


@dataclass
class KeyValueTable:
    """
    An asynchronously printed, two column table.
    
    "key_column_width" should be at least as large as the longest key, plus the
    length of the separator.
    """

    key_column_width: int
    total_width: Optional[int] = None
    separator = ": "

    def print_row(self, key: str, value: str):
        key_cell = key + self.separator
        if self.key_column_width < len(key_cell):
            warn(f"key_column_width should be at least {len(key_cell)}")
        if self.total_width is None:
            value_cell = value
        else:
            value_column_width = self.total_width - self.key_column_width
            # Make sure the multiline stirng stays within its cell, by rewrapping
            # and prepending spaces to all but the first line.
            value_cell = rewrap(value, value_column_width).replace(
                "\n", "\n" + " " * self.key_column_width
            )

        echo(key_cell.ljust(self.key_column_width) + value_cell, raw=True)


def rewrap(multiline: str, width=70, **TextWrap_kwargs) -> str:
    """ Linearize string, and wrap the result.
    
    :param multiline:  A multiline string as found in indented source code.
    :param width:  Max number of characters per line in the output.
    :param TextWrap_kwargs:  Keyword arguments passed to textwrap.TextWrap
            (from Python's standard library).
    :return:  A string without superfluous whitespace and with newlines so that
            it prints squarely.
    """
    oneline = linearize(multiline)
    return fill(oneline, width=width, **TextWrap_kwargs)


def linearize(multiline: str) -> str:
    """
    :param multiline:  A multiline string as found in indented source code.
    :return:  A stripped, one-line string. All newlines and multiple
            consecutive whitespace characters are replaced by a single space.
    """
    oneline = sub(r"\s+", " ", multiline)
    return oneline.strip()
