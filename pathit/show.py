"""Show PATH variable by line."""

import os
import typer

app = typer.Typer(add_completion=False, 
                  #does not work
                  help="Just show me my PATH variable.",
                  short_help="Just show the PATH.")


def get_var(name, sep):
    return os.environ[name].split(sep)


def print_sorted(sort: bool = False, includes: str | None = None):
    paths = get_var(name="PATH", sep=";")
    if sort:
        paths = sorted(paths)
    if includes is not None:
        paths = [path for path in paths if includes in path]
    print("\n".join(paths))


# https://github.com/tiangolo/typer/blob/3a7264cd56181690805f220cb44a0301c0fdf9f3/typer/main.py#L1053
# def run(function: Callable[..., Any]) -> None:
#     app = Typer(add_completion=False)
#     app.command()(function)
#     app()
def typer_app():
    typer.run(print_sorted)
