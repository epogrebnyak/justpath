import sys

import typer

from justpath.main import (
    DisplayOptions,
    SelectOptions,
    ModifyOptions,
    OutputFormat,
    print_path,
    PathDict,
)

typer_app = typer.Typer(add_completion=False, help="Explore PATH environment variable.")


@typer_app.command()
def show(
    raw: bool = False,
    sort: bool = False,
    invalid: bool = False,
    duplicates: bool = False,
    color: bool = True,
    line_numbers: bool = True,
    symlinks: bool = True,
    comment: bool = True,
    bare: bool = False,
    purge_invalid: bool = False,
    purge_duplicates: bool = False,
    correct: bool = False,
    format: OutputFormat = typer.Option(
        OutputFormat.LINES, help="Output format: lines, string, or json"
    ),
):
    """Display directories from the PATH environment variable."""
    if raw:
        print(PathDict.raw())
        sys.exit(0)
    so = SelectOptions(show_invalid=invalid, show_duplicates=duplicates, sort=sort)
    if bare:
        line_numbers = False
        symlinks = False
        comment = False
    do = DisplayOptions(
        use_color=color,
        line_numbers=line_numbers,
        symlinks=symlinks,
        comment=comment,
        format=format,
    )
    if correct:
        purge_invalid = True
        purge_duplicates = True
    mo = ModifyOptions(purge_invalid=purge_invalid, purge_duplicates=purge_duplicates)
    print_path(do, so, mo)
