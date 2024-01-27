"""Show and modify PATH variable.

Usage:
  pathit show [--sort] [--includes text] [--numbers]
  pathit suggest [--add DIR] [--drop n] 
"""

import os
import typer
from pathlib import Path
from colorama import Fore
from typing import Annotated

typer_app = typer.Typer(
    add_completion=False,
    # does not seem to work
    help="Just show me my PATH variable.",
    short_help="Just show the PATH.",
)


def sep():
    return ";" if os.name == "nt" else ":"


def get_enumerated_paths() -> list[tuple[int, str]]:
    return [(i, path) for i, path in enumerate(os.environ["PATH"].split(sep()))]


def get_paths() -> list[tuple[int, str]]:
    return [path for _, path in get_enumerated_paths()]


@typer_app.command()
def show(
    sort: bool = False,
    includes: str | None = None,
    numbers: bool = False,
    color: bool = True,
):
    """Show PATH and highlight existing directories."""
    paths = get_enumerated_paths()
    if sort:
        paths = sorted(paths, key=lambda p: p[1])
    if includes is not None:
        paths = [path for path in paths if includes in path[1]]
    for i, path in paths:
        prefix = ""
        if color:
            prefix = Fore.GREEN if os.path.exists(path) else Fore.RED
        if numbers:
            print(prefix + f"{i + 1}", path)
        else:
            print(prefix + path)


@typer_app.command()
def suggest():
    """Suggest a command to modify PATH."""


#     paths = get_paths()
#     for path in add:
#         if not Path(path).exists():
#             sys.exit("{path} does not exist")
#         if not Path(path).is_dir():
#             sys.exit("{path} is not a directory")
#         paths.append(str(path.resolve()))
#     print(sep().join(paths))
