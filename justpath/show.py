"""Explore PATH environment variable and demonstrate how to modify it."""

import os
import sys
from collections import UserDict
from json import dumps
from pathlib import Path
from typing import Annotated

import typer
from colorama import Fore


def get_paths() -> list[str]:
    return os.environ["PATH"].split(os.pathsep)


NumberedPaths = list[tuple[str, str]]  # should be a type vatiable?


class PathVar(UserDict[int, Path]):
    @classmethod
    def populate(cls):
        return cls([(i + 1, Path(p)) for i, p in enumerate(get_paths())])

    def drop(self, i: int):
        del self.data[i]

    def append(self, path: Path):
        key = 1 + self.max_key
        self.data[key] = path

    @property
    def max_key(self):
        return max(self.data.keys())

    def tuples(self) -> NumberedPaths:
        n = len(str(self.max_key))

        def offset(i: int) -> str:
            return str(i).rjust(n)

        return [(offset(i), str(p)) for i, p in self.data.items()]


def as_string(paths: NumberedPaths) -> str:
    return os.pathsep.join([str(path) for _, path in paths])


def is_valid(path: str) -> bool:
    return Path(path).exists() and Path(path).is_dir()


typer_app = typer.Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


@typer_app.command()
def raw():
    """Print PATH as is. Same as `justpath show --string`."""
    print(os.environ["PATH"])


@typer_app.command()
def stats(json: bool = False):
    """Number total and valid of directories in your PATH."""
    path_var = PathVar.populate()
    k = sum(map(is_valid, path_var.values()))
    if json:
        print(dumps(dict(total=len(path_var), valid=k)))
    else:
        print("Directories in your PATH")
        print("- total:", len(path_var))
        print("- valid:", k)


@typer_app.command()
def show(
    sort: Annotated[bool, typer.Option(help="Sort output alphabetically.")] = False,
    includes: str | None = None,  # Show paths that include a specific string.
    excludes: str | None = None,  # Show paths that exclude a specific string.
    purge: Annotated[bool, typer.Option(help="Exclude invalid directories.")] = False,
    expand: Annotated[
        bool, typer.Option(help="Expand environment variables if found inside PATH.")
    ] = False,
    string: Annotated[
        bool, typer.Option(help="Print a single string suitable for PATH content.")
    ] = False,
    display_numbers: Annotated[
        bool, typer.Option(help="Indicate directory order in PATH.")
    ] = True,
    color: Annotated[bool, typer.Option(help="Use color to highlight errors.")] = True,
    json: Annotated[bool, typer.Option(help="Format output as JSON.")] = False,
):
    """Show directories from PATH."""
    paths = PathVar.populate().tuples()
    if sort:
        paths = sorted(paths, key=lambda x: x[1])
    if includes is not None:
        paths = [path for path in paths if includes.lower() in path[1].lower()]
    if excludes is not None:
        paths = [path for path in paths if excludes.lower() not in path[1].lower()]
    if purge:
        paths = [path for path in paths if is_valid(path[1])]
        # TODO: control for duplicates, keep the first duplicate in a list
    if expand:  # probably a rare case
        paths = [(i, os.path.expandvars(path)) for i, path in paths]
    if string:
        print(as_string(paths))
        sys.exit(0)
    if json:
        print(dumps([str(path) for _, path in paths], indent=2))
        sys.exit(0)
    for i, path in paths:
        prefix = ""
        if color:
            prefix = Fore.RED
            if os.path.exists(path) and os.path.isdir(path):
                prefix = Fore.GREEN
        if display_numbers:
            postfix = ""
            if not os.path.exists(path):
                postfix = "(directory does not exist)"
            elif not os.path.isdir(path):
                postfix = "(it's a file, not a directory)"
            print(prefix + i, path, postfix)
        else:
            print(prefix + path)
