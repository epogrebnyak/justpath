"""Explore PATH environment variable and demonstrate how to modify it."""

import os
from collections import UserDict
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


def as_string(paths: list[tuple[int, Path]]) -> str:
    return os.pathsep.join([str(path) for _, path in paths])


def is_valid(path: Path) -> bool:
    return path.exists() and path.is_dir()


typer_app = Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


@typer_app.command()
def raw():
    """Print PATH as is. Same as `justpath show --string`."""
    print(os.environ["PATH"])


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
    includes: option("Show paths that include a specific string.", str) = "",  # type: ignore
    excludes: option("Show paths that do not include a specific string.", str) = "",  # type: ignore
    correct: option("Drop invalid paths.") = False,  # type: ignore
    strip: option("Hide extra information about paths.") = False,  # type: ignore
    color: option("Use color to highlight errors.") = True,  # type: ignore
    string: option("Print a single string suitable as PATH content.") = False,  # type: ignore
    json: option("Format output as JSON.") = False,  # type: ignore
):
    """Show directories from PATH."""
    paths = PathVar.populate().tuples()
    paths = modify_paths(paths, errors, sort, includes, excludes, correct)
    if string:
        print(as_string(paths))
    elif json:
        print(dumps([str(path) for _, path in paths], indent=2))
    else:
        print_paths(paths, color, strip)


def first(x):
    return x[0]


def second(x):
    return x[1]


def modify_paths(paths, errors, sort, includes, excludes, correct):
    paths = [(i, Path(os.path.realpath(path))) for i, path in paths]
    if sort:
        paths = sorted(paths, key=second)
    if errors:
        paths = [(i, path) for i, path in paths if not is_valid(path)]
    if includes:
        paths = [
            (i, path) for i, path in paths if includes.lower() in str(path).lower()
        ]
    if excludes:
        paths = [
            (i, path) for i, path in paths if excludes.lower() not in str(path).lower()
        ]
    if correct:
        paths = [(i, path) for i, path in paths if not is_valid(path)]
    # probably already handled by os.path.realpath
    # if expand:
    #     paths = [(i, os.path.expandvars(path)) for i, path in paths]
    return paths
    # TODO: control for duplicates, keep the first duplicate in a list


def print_paths(paths, color, strip):
    last_number = max([0] + [i for i, _ in paths])
    n = len(str(last_number))

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
