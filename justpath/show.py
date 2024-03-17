"""Explore PATH environment variable and demonstrate how to modify it."""

import os
import sys
from collections import Counter, UserDict
from dataclasses import dataclass
from json import dumps
from pathlib import Path
from typing import Annotated, Type

from colorama import Fore, Style
from typer import Option, Typer

from justpath.oneliners import print_alternatives


@dataclass
class Directory:
    original: str
    canonical: str
    resolved: str
    is_directory: bool
    does_exist: bool

    @staticmethod
    def to_canonical(path: str) -> str:
        fs = [
            os.path.expandvars,  # expands %name% or $NAME
            os.path.expanduser,  # expands ~
            os.path.normcase,  # to lowercase
        ]
        for f in fs:
            path = f(path)  # type: ignore
        return path

    @classmethod
    def from_path(cls, path: str):
        visible_path = cls.to_canonical(path)
        return cls(
            path,
            visible_path,
            os.path.realpath(visible_path),  # resolve symlinks
            os.path.isdir(visible_path),
            os.path.exists(visible_path),
        )

    @property
    def is_valid(self) -> bool:
        return self.is_directory and self.does_exist

    def includes(self, string):
        return string.lower() in self.canonical.lower()


class PathVariable(UserDict[int, Path]):
    @classmethod
    def from_list(cls, paths):
        result = cls()
        for i, path in enumerate(paths):
            result[i + 1] = Directory.from_path(path)
        return result

    @classmethod
    def populate(cls):
        return cls.from_list(os.environ["PATH"].split(os.pathsep))

    @property
    def paths(self):
        return [v.orginial for v in self.values()]

    def get_rows(self, getter):
        rows = []
        counter = Counter([getter(directory) for directory in self.values()])
        for i, directory in self.items():
            row = Row(i, directory, counter[getter(directory)])
            rows.append(row)
        return rows

    def to_rows(self, follow_symlinks: bool):
        getter = (lambda d: d.resolved) if follow_symlinks else (lambda d: d.original)
        return self.get_rows(getter)

    # not tested
    def drop(self, i: int):
        del self.data[i]

    # not tested
    def append(self, path: Path):
        key = 1 + max(self.keys())
        self.data[key] = Directory.from_path(path)


@dataclass
class Row:
    i: int
    directory: Directory
    count: int

    @property
    def error(self) -> Type[FileNotFoundError] | Type[NotADirectoryError] | None:
        if not self.directory.does_exist:
            return FileNotFoundError
        elif not self.directory.is_directory:
            return NotADirectoryError
        else:
            return None

    @property
    def has_error(self):
        return self.error is not None

    def __hash__(self):
        return hash(str(self.i) + self.directory.canonical)


def make_formatter(rows):
    # Number of digits in a line number, usually 1 or 2
    max_digits = len(str(max(row.i for row in rows))) if rows else 1

    def offset(i: int) -> str:
        return str(i).rjust(max_digits)

    return offset


typer_app = Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


def show_raw():
    """Print PATH as is."""
    print(os.environ["PATH"])


def show_stats(json: bool, follow_symlinks: bool):
    """Number of directories in your PATH."""
    path_var = PathVariable.populate()
    t = len(path_var)
    rows = path_var.to_rows(follow_symlinks)
    e = sum([1 for row in rows if row.has_error])
    d = sum([1 for row in rows if row.count > 1])
    if json:
        info = dict(total=t, invalid=e, duplicates=d)
        print(dumps(info))
    else:
        print(t, "directories in your PATH")
        if e == 0:
            print("All directories exist")
        else:
            print(e, "do" if e > 1 else "does", "not exist")
        print(d, "duplicate" + "s" if d > 1 else "")


def option(help_: str, t=bool):
    return Annotated[t, Option(help=help_)]


@typer_app.command()
def show(
    raw: option("Print PATH variable as is.") = False,  # type: ignore
    count: option("Print number of directories in your PATH.") = False,  # type: ignore
    sort: option("Sort output alphabetically.") = False,  # type: ignore
    invalid: option("Show invalid paths only.") = False,  # type: ignore
    purge_invalid: option("Exclude invalid paths.") = False,  # type: ignore
    duplicates: option("Show duplicate paths only.") = False,  # type: ignore
    purge_duplicates: option("Exclude duplicate paths.") = False,  # type: ignore
    correct: option("Exclude invalid and duplicate paths.") = False,  # type: ignore
    includes: option("Show paths that include a specific string.", str) = "",  # type: ignore
    excludes: option("Show paths that do not include a specific string.", str) = "",  # type: ignore
    follow_symlinks: option("Resolve symbolic links.", bool) = False,  # type: ignore
    bare: option("Provide minimal text output.") = False,  # type: ignore
    comments: option("Add extra information about paths.") = True,  # type: ignore
    numbers: option("Add line numbers.") = True,  # type: ignore
    color: option("Use color to highlight errors.") = True,  # type: ignore
    string: option("Print a single string suitable as PATH content.") = False,  # type: ignore
    json: option("Format output as JSON.") = False,  # type: ignore
    shell_equivalents: option("Print useful commands for bash, cmd and Powershell.") = False,  # type: ignore
):
    """Show directories from PATH."""
    if shell_equivalents:
        print_alternatives()
        sys.exit(0)
    if raw:
        show_raw()
        sys.exit(0)
    if count:
        show_stats(json, follow_symlinks)
        sys.exit(0)
    path_var = PathVariable.populate()
    rows = path_var.to_rows(follow_symlinks)
    if correct:
        purge_duplicates = True
        purge_invalid = True
    rows = modify_rows(
        rows,
        sort,
        duplicates,
        purge_duplicates,
        invalid,
        purge_invalid,
        includes,
        excludes,
        follow_symlinks,
    )
    paths = [str(row.directory.original) for row in rows]
    if bare:
        comments = False
        numbers = False
        color = False
    if string:
        print(os.pathsep.join(paths))
    elif json:
        print(dumps(paths, indent=2))
    else:
        offset = make_formatter(rows)
        for row in rows:
            items = [
                (get_color(row) if color else "") + (offset(row.i) if numbers else ""),
                str(row.directory.original),
                get_comment(row) if comments else "",
            ]
            print(" ".join(item for item in items if item))
    if color:
        print(Style.RESET_ALL, end="")


def modify_rows(
    rows,
    sort,
    duplicates,
    purge_duplicates,
    invalid,
    purge_invalid,
    includes,
    excludes,
    follow_symlinks,
):
    if sort:
        rows = sorted(rows, key=lambda r: r.directory.canonical)
    if duplicates:
        rows = [row for row in rows if row.count > 1]
    if purge_duplicates:
        rows = remove_duplicates(rows, follow_symlinks)
    if invalid:
        rows = [row for row in rows if row.has_error]
    if purge_invalid:
        rows = [row for row in rows if not row.has_error]
    if includes:
        rows = [row for row in rows if row.directory.includes(includes)]
    if excludes:
        rows = [row for row in rows if not row.directory.includes(excludes)]
    return rows


def get_color(row: Row):
    """Get color modifier for regular, invalid or duplicate directories."""
    if row.has_error:
        return Fore.RED
    elif row.count > 1:
        return Fore.YELLOW
    return Fore.GREEN


def get_comment(row: Row) -> str:
    """Create a string that tells about a type of error or property encountered."""
    items = []
    if row.directory.canonical != row.directory.resolved:
        items.append(f"resolves to {row.directory.resolved}")
    if row.error == FileNotFoundError:
        items.append("directory does not exist")
    elif row.error == NotADirectoryError():
        items.append("not a directory")
    if (n := row.count) > 1:
        items.append(f"duplicates: {n}")
    if items:
        return "(" + ", ".join(items) + ")"
    return ""


def remove_duplicates(rows, follow_symlinks):
    seen = set()
    result = []
    for row in rows:
        if follow_symlinks:
            p = row.directory.resolved
        else:
            p = row.directory.original
        if p not in seen:
            seen.add(p)
            row.count = 1
            result.append(row)
    return result
