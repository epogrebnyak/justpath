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
    raw: bool = typer.Option(False, help="Print raw PATH variable content."),
    count: bool = typer.Option(False, help="Show count of directories in PATH."),
    sort: bool = typer.Option(False, help="Sort directories alphabetically."),
    invalid: bool = typer.Option(False, help="Show only invalid directories."),
    duplicates: bool = typer.Option(False, help="Show only duplicate directories."),
    color: bool = typer.Option(True, help="Use colored output."),
    line_numbers: bool = typer.Option(True, help="Show line numbers."),
    symlinks: bool = typer.Option(True, help="Show symlinks."),
    comment: bool = typer.Option(True, help="Show error messages."),
    bare: bool = typer.Option(False, help="Minimal output (no numbers, symlinks and comments)."),
    purge_invalid: bool = typer.Option(False, help="Remove invalid directories from PATH."),
    purge_duplicates: bool = typer.Option(False, help="Remove duplicate directories from PATH."),
    correct: bool = typer.Option(False, help="Remove both invalid and duplicate directories."),
    format: OutputFormat = typer.Option(
        OutputFormat.LINES, help="Output format: lines, string, or json"
    ),
    includes: list[str] = typer.Option(
        default_factory=list, help="Only show directories that contain these strings."
    ),
    excludes: list[str] = typer.Option(
        default_factory=list, help="Skip directories that contain these strings."
    ),
    version: bool = typer.Option(False, help="Show justpath version.")
) -> None:
    """Display directories from the PATH environment variable."""
    if version:
        from justpath import __version__

        print(__version__)
        sys.exit(0)
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
