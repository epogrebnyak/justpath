"""Explore PATH environment variable and demonstrate how to modify it."""

import os
import sys
from collections import Counter, UserDict
from dataclasses import dataclass
from json import dumps
from os.path import realpath
from pathlib import Path
from typing import Annotated, Type

from colorama import Fore, Style
from typer import Option, Typer
from justpath.oneliners import print_alternatives
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Directory:
    original: str
    resolved: str
    is_directory: bool
    does_exist: bool

    @classmethod
    def from_path(cls, path: str):
        return cls(
            os.path.normcase(path),
            os.path.realpath(path),
            os.path.isdir(path),
            os.path.exists(path),
        )


from typing import TypedDict


def identity(x):
    return x


class PathVariable(TypedDict):
    line_number: int
    directory: tuple[Directory, int | None]

    @classmethod
    def populate(cls):
        result = cls()
        for i, path in enumerate(os.environ["PATH"].split(os.pathsep)):
            result[i + 1] = (Directory.from_path(path), None)
        return result

    @property
    def paths(self):
        return [v[0] for v in self.values()]

    def count(self, f=identity):
        counter = Counter(map(f, self.paths))
        cls = self.__cls__
        return cls(
            (line_number, (d, counter[f(d)])) for line_number, (d, _) in self.items()
        )

    def count_by_realpath(self):
        pass


# pv = PathVariable.populate()
# print(isinstance(pv, PathVariable))


class PathVar(UserDict[int, Path]):
    @classmethod
    def from_list(cls, paths):
        return cls([(i + 1, Path(p)) for i, p in enumerate(paths)])

    @classmethod
    def populate(cls):
        return cls.from_list(os.environ["PATH"].split(os.pathsep))

    def drop(self, i: int):
        del self.data[i]

    def append(self, path: Path):
        key = 1 + max(self.keys())
        self.data[key] = path

    @property
    def max_digits(self) -> int:
        """Number of digits in a line number, usually 1 or 2."""
        return len(str(max(self.keys()))) if self.keys() else 0

    def offset(self, i: int):
        return str(i).rjust(self.max_digits)

    def to_rows(self, follow_symlinks: bool) -> list["Row"]:
        getter = resolve if follow_symlinks else as_is
        counter = Counter([getter(path) for path in self.values()])

        def make_row(i, path):
            return Row(i, path, counter[getter(path)])

        return [make_row(i, path) for i, path in self.items()]


def resolve(path: Path) -> str:
    return str(path.resolve()).lower()


def as_is(path: Path) -> str:
    return str(path).lower()


@dataclass
class Row:
    i: int
    path: Path
    count: int

    @property
    def error(self) -> Type[FileNotFoundError] | Type[NotADirectoryError] | None:
        if not os.path.exists(self.path):
            return FileNotFoundError
        elif not os.path.isdir(self.path):
            return NotADirectoryError
        else:
            return None

    @property
    def has_error(self):
        return self.error is not None

    def __hash__(self):
        return hash(realpath(self.path).lower())


typer_app = Typer(
    add_completion=False, help="Explore PATH environment variable on Windows and Linux."
)


def show_raw():
    """Print PATH as is."""
    print(os.environ["PATH"])


def show_stats(json: bool, follow_symlinks: bool):
    """Number of directories in your PATH."""
    path_var = PathVar.populate()
    t = len(path_var)
    rows = path_var.to_rows(follow_symlinks)
    e = sum([1 for row in rows if row.has_error])
    d = sum([1 for row in rows if row.count > 1])
    if json:
        info = dict(total=t, invalid=e, duplicates=d)
        print(dumps(info))
    else:
        print(t, "directories in your PATH")
        if e == 0:
            print("All directories exist")
        else:
            print(e, "do" if e > 1 else "does", "not exist")
        print(d, "duplicate" + "s" if d > 1 else "")


def option(help_: str, t=bool):
    return Annotated[t, Option(help=help_)]


@typer_app.command()
def show(
    raw: option("Print PATH variable as is.") = False,  # type: ignore
    count: option("Print number of directories in your PATH.") = False,  # type: ignore
    sort: option("Sort output alphabetically.") = False,  # type: ignore
    invalid: option("Show invalid paths only.") = False,  # type: ignore
    purge_invalid: option("Exclude invalid paths.") = False,  # type: ignore
    duplicates: option("Show duplicate paths only.") = False,  # type: ignore
    purge_duplicates: option("Exclude duplicate paths.") = False,  # type: ignore
    correct: option("Exclude invalid and duplicate paths.") = False,  # type: ignore
    includes: option("Show paths that include a specific string.", str) = "",  # type: ignore
    excludes: option("Show paths that do not include a specific string.", str) = "",  # type: ignore
    follow_symlinks: option("Resolve symbolic links.", bool) = False,  # type: ignore
    bare: option("Provide minimal text output.") = False,  # type: ignore
    comments: option("Add extra information about paths.") = True,  # type: ignore
    numbers: option("Add line numbers.") = True,  # type: ignore
    color: option("Use color to highlight errors.") = True,  # type: ignore
    string: option("Print a single string suitable as PATH content.") = False,  # type: ignore
    json: option("Format output as JSON.") = False,  # type: ignore
    shell_equivalents: option("Print useful commands for bash, cmd and Powershell.") = False,  # type: ignore
):
    """Show directories from PATH."""
    if shell_equivalents:
        print_alternatives()
        sys.exit(0)
    if raw:
        show_raw()
        sys.exit(0)
    if count:
        show_stats(json, follow_symlinks)
        sys.exit(0)
    path_var = PathVar.populate()
    rows = path_var.to_rows(follow_symlinks)
    if correct:
        purge_duplicates = True
        purge_invalid = True
    rows = modify_rows(
        rows,
        sort,
        duplicates,
        purge_duplicates,
        invalid,
        purge_invalid,
        includes,
        excludes,
        follow_symlinks,
    )
    paths = [str(row.path) for row in rows]
    if bare:
        comments = False
        numbers = False
        color = False
    if string:
        print(os.pathsep.join(paths))
    elif json:
        print(dumps(paths, indent=2))
    else:
        for row in rows:
            items = [
                get_color(row) if color else "",
                path_var.offset(row.i) if numbers else "",
                str(row.path),
                get_comment(row) if comments else "",
            ]
            print("".join(item for item in items if item))
    if color:
        print(Style.RESET_ALL, end="")


def modify_rows(
    rows,
    sort,
    duplicates,
    purge_duplicates,
    invalid,
    purge_invalid,
    includes,
    excludes,
    follow_symlinks,
):
    if sort:
        rows = sorted(rows, key=lambda r: realpath(r.path))
    if duplicates:
        rows = [row for row in rows if row.count > 1]
    if purge_duplicates:
        rows = remove_duplicates(rows, follow_symlinks)
    if invalid:
        rows = [row for row in rows if row.has_error]
    if purge_invalid:
        rows = [row for row in rows if not row.has_error]
    if includes:
        rows = [row for row in rows if includes.lower() in realpath(row.path).lower()]
    if excludes:
        rows = [
            row for row in rows if excludes.lower() not in realpath(row.path).lower()
        ]
    return rows


def get_color(row: Row):
    """Get color modifier for regular, invalid or duplicate directories."""
    if row.has_error:
        return Fore.RED
    elif row.count > 1:
        return Fore.YELLOW
    return Fore.GREEN


def get_comment(row: Row) -> str:
    """Create a string that tells about a type of error or property encountered."""
    items = []
    if row.path.is_symlink():
        items.append(f"resolves to {row.path.resolve()}")
    if row.error == FileNotFoundError:
        items.append("directory does not exist")
    elif row.error == NotADirectoryError():
        items.append("not a directory")
    if (n := row.count) > 1:
        items.append(f"duplicates: {n}")
    if items:
        return "(" + ", ".join(items) + ")"
    return ""


def remove_duplicates(rows, follow_symlinks):
    seen = set()
    result = []
    for row in rows:
        if follow_symlinks:
            p = resolve(row.path)
        else:
            p = as_is(row.path)
        if p not in seen:
            seen.add(p)
            row.count = 1
            result.append(row)
    return result
