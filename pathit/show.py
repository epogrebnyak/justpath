"""Explore PATH environment variable and demonstrate how to modify it."""

import os
from collections import UserDict
from pathlib import Path

import typer
from colorama import Fore


def sep():
    return ";" if os.name == "nt" else ":"


def get_paths() -> list[str]:
    return os.environ["PATH"].split(sep())


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

    def tuples(self):
        n = len(str(self.max_key))

        def offset(i: int) -> str:
            return str(i).rjust(n)

        return [(offset(i), str(p)) for i, p in self.data.items()]


typer_app = typer.Typer(
    add_completion=False,
)


@typer_app.command()
def raw():
    print(os.environ["PATH"])


@typer_app.command()
def show(
    sort: bool = False,
    includes: str | None = None,
    excludes: str | None = None,
    display_numbers: bool = True,
    color: bool = True,
    purge: bool = False,
    command: bool = False,
    expand: bool = False,
    only_errors: bool = False,
):
    """Show directories from PATH."""
    paths = PathVar.populate().tuples()
    if sort:
        paths = sorted(paths, key=lambda x: x[1])
    if includes is not None:
        paths = [path for path in paths if includes in path[1]]
    if excludes is not None:
        paths = [path for path in paths if excludes not in path[1]]
    if not command:
        for i, path in paths:
            prefix = ""
            if color:
                prefix = Fore.GREEN if os.path.exists(path) else Fore.RED
            if display_numbers:
                postfix = "" if os.path.exists(path) else "(directory does not exist)"
                print(prefix + i, path, postfix)
            else:
                print(prefix + path)
    else:
        print("This will show `export` or `set` command.")
    if purge:
        print("This will drop non-existent or duplicate directories.")
    if expand:
        print("This will resolve directory names.")
