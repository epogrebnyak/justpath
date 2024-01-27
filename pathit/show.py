import os
import typer

app = typer.Typer()


def get_var(name, sep):
    return os.environ[name].split(sep)


def print_sorted(sort: bool = False, includes: str | None = None):
    paths = get_var(name="PATH", sep=";")
    if sort:
        paths = sorted(paths)
    if includes is not None:
        paths = [path for path in paths if includes in path]
    print("\n".join(paths))


def typer_app():
    typer.run(print_sorted)
