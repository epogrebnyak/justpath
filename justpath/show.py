"""Explore PATH environment variable and demonstrate how to modify it."""

import os
import sys
from collections import Counter, UserDict
from dataclasses import dataclass
from json import dumps
from pathlib import Path
from typing import Annotated

from colorama import Fore
from typer import Option, Typer


def get_paths() -> list[str]:
    return os.environ["PATH"].split(os.pathsep)


class PathVar(UserDict[int, Path]):
    @classmethod
    def populate(cls):
        return cls([(i + 1, Path(p)) for i, p in enumerate(get_paths())])

    def drop(self, i: int):
        del self.data[i]

    def append(self, path: Path):
        key = 1 + max(self.keys())
        self.data[key] = path

    def tuples(self) -> list[tuple[int, Path]]:
        return [(i, p) for i, p in self.data.items()]

    @property
    def max_digits(self):
        return len(str(max(self.keys()))) if self.keys() else 0


def as_string(paths: list[tuple[int, Path]]) -> str:
    return os.pathsep.join([str(path) for _, path in paths])


def is_valid(path: Path) -> bool:
    return path.exists() and path.is_dir()


@dataclass
class Duplicate:
    count: int


@dataclass
class Row:
    i: int
    path: Path
    count: int
    error: FileNotFoundError | NotADirectoryError | None = None


def get_error(path: Path):
    if not os.path.exists(path):
        return FileNotFoundError
    elif not os.path.isdir(path):
        return NotADirectoryError
    else:
        return None


def to_rows(path_var: PathVar) -> list[Row]:
    counter = Counter([os.path.realpath(p) for p in path_var.values()])
    rows = []
    for i, path in path_var.items():
        row = Row(i, path, counter[os.path.realpath(path)], get_error(path))
        rows.append(row)
    return rows


typer_app = Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


@typer_app.command()
def raw():
    """Print PATH as is. Same as `justpath show --string`."""
    print(os.environ["PATH"])


def print_row(row, color, n):
    def offset(k: int) -> str:
        return str(k).rjust(n)

    modifier = ""
    if color:
        modifier = Fore.GREEN
        if row.error is not None:
            modifier = Fore.RED
        elif row.count > 1:
            modifier = Fore.YELLOW
    postfixes = []
    if row.error == FileNotFoundError:
        postfixes.append("directory does not exist")
    elif row.error == NotADirectoryError():
        postfixes.append("not a directory")
    if (n := row.count) > 1:
        postfixes.append(f"duplicates: {n}")
    last = "(" + ", ".join(postfixes) + ")" if postfixes else ""
    print(modifier + offset(row.i), row.path, last)


@typer_app.command()
def rows():
    path_var = PathVar.populate()
    rows = to_rows(PathVar.populate())
    for row in rows:
        print_row(row, color=True, n=path_var.max_digits)


@typer_app.command()
def count(json: bool = False):
    """Number of directories in your PATH."""
    path_var = PathVar.populate()
    t = len(path_var)
    k = sum(map(is_valid, path_var.values()))
    if json:
        print(dumps(dict(total=t, valid=k, errors=t - k)))
    else:
        print("Directories in your PATH")
        print("  Total: ", t)
        print("  Valid: ", k)
        print("  Errors:", t - k)


def option(help_: str, t=bool):
    return Annotated[t, Option(help=help_)]


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
    """Show directories from PATH."""
    paths = PathVar.populate().tuples()
    paths = modify_paths(paths, duplicates, errors, sort, includes, excludes, correct)
    if string:
        print(as_string(paths))
    elif json:
        print(dumps([str(path) for _, path in paths], indent=2))
    else:
        print_paths(paths, color, strip)


def second(x):
    return x[1]


def modify_paths(paths, duplicates, errors, sort, includes, excludes, correct):
    paths = [(i, Path(os.path.realpath(path))) for i, path in paths]
    if duplicates:
        sys.exit("`--duplicates` flag not implemented yet.")
    if sort:
        paths = sorted(paths, key=second)
    if includes:
        paths = [(i, p) for i, p in paths if includes.lower() in str(p).lower()]
    if excludes:
        paths = [(i, p) for i, p in paths if excludes.lower() not in str(p).lower()]
    if errors:
        paths = [(i, path) for i, path in paths if not is_valid(path)]
    if correct:
        paths = [(i, path) for i, path in paths if is_valid(path)]
    return paths


def n_positions(xs: list[int]) -> int:
    if xs:
        return len(str(max(xs)))
    else:
        # sometimes xs may be empty
        return 0


def print_paths(paths, color, strip):
    n = n_positions([i for i, _ in paths])

    def offset(k: int) -> str:
        return str(k).rjust(n)

    for i, path in paths:
        modifier = ""
        if color:
            modifier = Fore.RED
            if os.path.exists(path) and os.path.isdir(path):
                modifier = Fore.GREEN
        if strip:
            print(modifier + str(path))
        else:
            postfix = ""
            if not os.path.exists(path):
                postfix = "(directory does not exist)"
            elif not os.path.isdir(path):
                postfix = "(not a directory)"
            print(modifier + offset(i), path, postfix)
