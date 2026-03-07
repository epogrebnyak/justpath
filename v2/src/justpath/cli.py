import sys

import typer

from justpath.main import (
    DisplayOptions,
    ModifyOptions,
    OutputFormat,
    PathDict,
    SelectOptions,
    print_path,
    print_stats,
)

typer_app = typer.Typer(add_completion=False, help="Explore PATH environment variable.")


@typer_app.command()
def show(
    count: bool = False,
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
    includes: list[str] = typer.Option(
        default_factory=list, help="Only show directories that contain this string."
    ),
    excludes: list[str] = typer.Option(
        default_factory=list, help="Skip directories that contain this string."
    ),
) -> None:
    """Display directories from the PATH environment variable."""
    if count:
        print_stats(holder=PathDict.populate(), use_json=format == OutputFormat.JSON)
        sys.exit(0)
    if raw:
        print(PathDict.raw())
        sys.exit(0)
    so = SelectOptions(
        show_invalid=invalid,
        show_duplicates=duplicates,
        sort=sort,
        symlinks=symlinks,
        includes=includes,
        excludes=excludes,
    )
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
