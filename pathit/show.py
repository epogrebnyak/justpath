"""Show and modify PATH variable.

Usage:
  pathit show [--sort] [--includes text] [--only-exist | --only-ghost] [--numbers]
  pathit add PATH
  pathit drop n [--yes]
"""

import os
import typer
from pathlib import Path
from colorama import Fore

app = typer.Typer(add_completion=False, 
                  #does not work
                  help="Just show me my PATH variable.",
                  short_help="Just show the PATH.")


def get_paths() -> list[tuple[int, str]]:
    sep = ";" if os.name == 'nt' else ":"
    return [(i, path) for i, path in enumerate(os.environ["PATH"].split(sep))]


def print_sorted(sort: bool = False, 
                 includes: str | None = None,
                 show_number: bool = False):
    paths = get_paths() 
    if sort:
        paths = sorted(paths, key=lambda p: p[1])
    if includes is not None:
        paths = [path for path in paths if includes in path[1]]
    for i, path in paths:
        prefix = Fore.GREEN if os.path.exists(path) else Fore.RED
        if show_number:
            print(prefix, i+1, path)
        else:
            print(prefix, path)    


# https://github.com/tiangolo/typer/blob/3a7264cd56181690805f220cb44a0301c0fdf9f3/typer/main.py#L1053
# def run(function: Callable[..., Any]) -> None:
#     app = Typer(add_completion=False)
#     app.command()(function)
#     app()
def typer_app():
    typer.run(print_sorted)
