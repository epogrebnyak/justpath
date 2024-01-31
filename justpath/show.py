"""Explore PATH environment variable and demonstrate how to modify it."""

import os
from collections import Counter, UserDict
from dataclasses import dataclass
from json import dumps
from os.path import realpath
from pathlib import Path
from typing import Annotated, Type

from colorama import Fore
from typer import Option, Typer


class PathVar(UserDict[int, Path]):
    @classmethod
    def populate(cls):
        paths = os.environ["PATH"].split(os.pathsep)
        return cls([(i + 1, Path(p)) for i, p in enumerate(paths)])

    def drop(self, i: int):
        del self.data[i]

    def append(self, path: Path):
        key = 1 + max(self.keys())
        self.data[key] = path

    @property
    def max_digits(self):
        return len(str(max(self.keys()))) if self.keys() else 0


@dataclass
class Row:
    i: int
    path: Path
    count: int

    # maybe cache it
    @property
    def error(self) -> Type[FileNotFoundError] | Type[NotADirectoryError] | None:
        # good case for Err, Ok
        if not os.path.exists(self.path):
            return FileNotFoundError
        elif not os.path.isdir(self.path):
            return NotADirectoryError
        else:
            return None


def to_rows(path_var: PathVar) -> list[Row]:
    counter = Counter([realpath(p) for p in path_var.values()])
    rows = []
    for i, path in path_var.items():
        row = Row(i, path, counter[realpath(path)])
        rows.append(row)
    return rows


typer_app = Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


@typer_app.command()
def raw():
    """Print PATH as is. Same as `justpath show --string`."""
    print(os.environ["PATH"])


def get_color(row: Row):
    if row.error is not None:
        return Fore.RED
    elif row.count > 1:
        return Fore.YELLOW
    return Fore.GREEN


def get_postfix(row: Row) -> str:
    items = []
    if row.error == FileNotFoundError:
        items.append("directory does not exist")
    elif row.error == NotADirectoryError():
        items.append("not a directory")
    if (n := row.count) > 1:
        items.append(f"duplicates: {n}")
    if items:
        return "(" + ", ".join(items) + ")"
    return ""


def print_row(row: Row, color: bool, n: int):
    modifier = get_color(row) if color else ""
    postfix = get_postfix(row)
    print(modifier + str(row.i).rjust(n), str(row.path), postfix)


@typer_app.command()
def lines():
    """Print PATH line by line."""
    path_var = PathVar.populate()
    rows = to_rows(PathVar.populate())
    for row in rows:
        print_row(row, color=True, n=path_var.max_digits)


@typer_app.command()
def count(json: bool = False):
    """Number of directories in your PATH."""
    path_var = PathVar.populate()
    t = len(path_var)
    k = sum([1 for row in to_rows(path_var) if row.error is not None])
    if json:
        print(dumps(dict(total=t, valid=k, errors=t - k)))
    else:
        print("Directories in your PATH")
        print("  Total: ", t)
        print("  Valid: ", k)
        print("  Errors:", t - k)


def option(help_: str, t=bool):
    return Annotated[t, Option(help=help_)]


# maybe split into inspect and make
@typer_app.command()
def show(
    sort: option("Sort output alphabetically.") = False,  # type: ignore
    errors: option("Show invalid paths only.") = False,  # type: ignore
    duplicates: option("Show duplicate paths only.") = False,  # type: ignore
    correct: option("Drop invalid or duplicate paths.") = False,  # type: ignore
    includes: option("Show paths that include a specific string.", str) = "",  # type: ignore
    excludes: option("Show paths that do not include a specific string.", str) = "",  # type: ignore
    strip: option("Hide extra information about paths.") = False,  # type: ignore
    color: option("Use color to highlight errors.") = True,  # type: ignore
    string: option("Print a single string suitable as PATH content.") = False,  # type: ignore
    json: option("Format output as JSON.") = False,  # type: ignore
):
    """Show directories from PATH and optionally apply filters."""
    path_var = PathVar.populate()
    rows = to_rows(path_var)
    rows = modify_rows(rows, duplicates, errors, sort, includes, excludes, correct)
    paths = [str(row.path) for row in rows]
    if string:
        print(os.pathsep.join(paths))
    elif json:
        print(dumps(paths, indent=2))
    else:
        for row in rows:
            if strip:
                modifier = get_color(row) if color else ""
                print(modifier + str(row.path))
            else:
                print_row(row, color, path_var.max_digits)


def modify_rows(rows, duplicates, errors, sort, includes, excludes, correct):
    if duplicates:
        rows = [row for row in rows if row.count > 1]
    if errors:
        rows = [row for row in rows if row.error is not None]
    if sort:
        rows = sorted(rows, key=lambda r: realpath(r.path))
    if includes:
        rows = [row for row in rows if includes.lower() in realpath(row.path).lower()]
    if excludes:
        rows = [
            row for row in rows if excludes.lower() not in realpath(row.path).lower()
        ]
    if correct:
        rows = [row for row in rows if row.error is None]
        # TODO: drop duplicate paths from the end
    return rows
