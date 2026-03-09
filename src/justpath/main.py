"""Explore PATH environment variable."""

import json
import os
from abc import ABC
from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable, Iterator
from typing import Any

from rich.console import Console
from rich.text import Text


class OutputFormat(str, Enum):
    """Output format options."""

    LINES = "lines"
    STRING = "string"
    JSON = "json"


@dataclass
class Directory:
    """Represents a directory path."""

    raw: str
    canonical: str
    resolved: str  # resolved symlinks
    is_directory: bool
    exists: bool

    @staticmethod
    def to_canonical(path: str) -> str:
        """Convert a path by expanding variables and normalizing case."""
        funcs = [
            os.path.expandvars,  # expands %name% or $NAME
            os.path.expanduser,  # expands ~
            os.path.normcase,  # change to lowercase
        ]
        for f in funcs:
            path = f(path)  # type: ignore
        return path

    @classmethod
    def from_string(cls, raw: str) -> "Directory":
        """Create a Directory instance from string."""
        visible_path = cls.to_canonical(raw)
        return cls(
            raw,
            visible_path,
            os.path.realpath(visible_path),
            os.path.isdir(visible_path),
            os.path.exists(visible_path),
        )

    @property
    def is_valid(self) -> bool:
        """Check if the directory path exists and it is not a file."""
        return self.exists and self.is_directory

    def to_dict(self) -> dict[str, str | bool]:
        """Return a dictionary representation of the Directory."""
        return {
            "raw": self.raw,
            "canonical": self.canonical,
            "resolved": self.resolved,
            "is_valid": self.is_valid,
        }


class PathDict(UserDict[int, Directory]):
    """Represents directories from PATH."""

    @staticmethod
    def raw() -> str:
        """Return raw PATH variable."""
        try:
            return os.environ["PATH"]
        except KeyError:
            raise EnvironmentError("PATH variable not found")

    @classmethod
    def from_list(cls, paths: list[str]) -> "PathDict":
        """Create a PathDict from a list of directory paths."""
        dirs = {i + 1: Directory.from_string(p) for i, p in enumerate(paths)}
        return cls(dirs)

    @classmethod
    def populate(cls) -> "PathDict":
        """Create a PathDict by parsing the PATH environment variable."""
        paths = cls.raw().split(os.pathsep)
        return cls.from_list(paths)

    def to_string(self) -> str:
        return os.pathsep.join(d.raw for d in self.values())

    def to_json(self) -> str:
        """Return JSON representation of PATH entries."""
        serial = {i: d.to_dict() for i, d in self.items()}
        return json.dumps(serial, indent=2)

    def filter_values(self, f: Callable[[Directory], bool]) -> None:
        """Return a new PathDict with values filtered with f."""
        self.data = {k: v for k, v in self.items() if f(v)}

    def _count_duplicates(self, path: str, attr: str) -> int:
        return sum(1 for d in self.values() if getattr(d, attr) == path)

    def create_counter(self, d: Directory) -> "Counter":
        """Return a Counter with raw and resolved path counts."""
        r1 = self._count_duplicates(d.raw, "raw")
        r2 = self._count_duplicates(d.resolved, "resolved")
        return Counter(r1, r2)

    def path_items(self) -> Iterator["PathItem"]:
        """Create a PathItem for a given directory."""
        for i, directory in self.items():
            counter = self.create_counter(directory)
            yield PathItem(i, directory, counter)

    def _sorting(
        self, f_key: Callable[[tuple[int, Directory]], Any]
    ) -> dict[int, Directory]:
        """Sort inline by a given key function."""
        return dict(sorted(self.items(), key=f_key))

    def sort_raw(self) -> None:
        """Sort inline by raw path."""
        self.data = self._sorting(lambda x: x[1].raw)

    def sort_resolved(self) -> None:
        """Sort inline by resolved path (useful for grouping duplicates)."""
        self.data = self._sorting(lambda x: (x[1].resolved, x[1].raw))

    def purge_invalid(self) -> None:
        """Purge invalid directories."""
        self.filter_values(lambda d: d.is_valid)

    def purge_duplicates(self) -> None:
        """Purge duplicate directories."""
        # keep only the first occurrence of a duplicate directory
        seen_resolved = set()

        def is_unique(d: Directory) -> bool:
            if d.resolved in seen_resolved:
                return False
            seen_resolved.add(d.resolved)
            return True

        self.filter_values(is_unique)

    def purge(self, mo: "ModifyOptions") -> "PathDict":
        """Purge invalid and/or duplicate directories."""
        if mo.purge_invalid:
            self.purge_invalid()
        if mo.purge_duplicates:
            self.purge_duplicates()
        return self

    def select(self, so: "SelectOptions") -> "PathDict":
        """Modify PathDict in place based on SelectOptions."""
        # sorting (behaviour affected by --symlinks flag)
        if so.sort:
            if so.symlinks:
                self.sort_resolved()
            else:
                self.sort_raw()

        # process --includes and --excludes filters (behaviour affected by --symlinks flag as well)
        for word in so.includes:
            if so.symlinks:
                self.filter_values(lambda d: word.lower() in d.resolved)
            else:
                self.filter_values(lambda d: word in d.raw)
        for word in so.excludes:
            print(word)
            if so.symlinks:
                self.filter_values(lambda d: word.lower() not in d.resolved)
            else:
                self.filter_values(lambda d: word not in d.raw)

        # deal with --invalid and --duplicates flag
        def is_invalid(d: Directory) -> bool:
            return not d.is_valid

        def is_duplicate(d: Directory) -> bool:
            return not self.create_counter(d).is_ok

        if so.show_invalid and so.show_duplicates:
            self.filter_values(lambda d: is_invalid(d) or is_duplicate(d))
        elif so.show_invalid:
            self.filter_values(is_invalid)
        elif so.show_duplicates:
            self.filter_values(is_duplicate)
        return self


@dataclass
class Counter:
    """Stores number of occurrences of raw and resolved paths."""

    raw: int
    resolved: int

    @property
    def is_ok(self) -> bool:
        """Check if the path appears exactly once in both raw and resolved forms."""
        return self.raw == 1 and self.resolved == 1

    @property
    def is_duplicate(self) -> bool:
        """Check if the path appears more than once in either raw or resolved forms."""
        return self.raw > 1 or self.resolved > 1


class PathStatus(ABC):

    @property
    def color(self) -> str:
        """Return color based on error type."""
        match self:
            case Error(level=Level.CRITICAL, message=_):
                return "red"
            case Error(level=Level.MINOR, message=_):
                return "gold3"
            case NoError():
                return "green"
            case _:
                raise ValueError("Unknown status type")


class NoError(PathStatus):
    pass


class Level(Enum):
    CRITICAL = "critical"
    MINOR = "minor"


@dataclass
class Error(PathStatus):
    level: Level
    message: str


@dataclass
class PathItem:
    i: int
    dir: Directory
    duplicates: Counter

    def get_status(self) -> PathStatus:
        """Return an error message or no error for directory."""
        if not self.dir.exists:
            return Error(Level.CRITICAL, "directory does not exist")
        if not self.dir.is_directory:
            return Error(Level.CRITICAL, "not a directory")
        if (n := self.duplicates.resolved) > 1:
            return Error(Level.MINOR, f"{n} duplicates")
        return NoError()


@dataclass
class ModifyOptions:
    purge_invalid: bool
    purge_duplicates: bool


@dataclass
class SelectOptions:
    """Used in PathDict.select to modify the PathDict in place based on these options."""

    show_invalid: bool
    show_duplicates: bool
    sort: bool
    symlinks: bool
    includes: list[str]
    excludes: list[str]


@dataclass
class DisplayOptions:
    line_numbers: bool
    symlinks: bool
    comment: bool
    use_color: bool
    format: OutputFormat

    def apply(self, line: PathItem, max_digits: int) -> Text:
        """Format PathItem based on display options."""
        text = Text()
        if self.line_numbers:
            lineno = str(line.i).rjust(max_digits)
            text.append(lineno, style="grey74")
        status = line.get_status()
        space = " " if self.line_numbers else ""
        text.append(space + line.dir.raw, style=status.color)
        if self.symlinks and line.dir.resolved != line.dir.raw:
            text.append(f" → {line.dir.resolved}", style="steel_blue1")
        if self.comment:
            match status:
                case Error(_, message):
                    message = " (" + status.message + ")"
                    text.append(message, style="grey74")
                case _:
                    pass
        return text if self.use_color else Text(text.plain)


def print_path(do: DisplayOptions, so: SelectOptions, mo: ModifyOptions) -> None:
    """Print the directories in PATH with their validation status."""
    holder = PathDict.populate().select(so).purge(mo)
    match do.format:
        case OutputFormat.STRING:
            print(holder.to_string())
        case OutputFormat.JSON:
            print(holder.to_json())
        case OutputFormat.LINES:
            max_digits = len(str(len(holder)))
            console = Console()
            for p in holder.path_items():
                message = do.apply(p, max_digits)
                console.print(message)


def print_stats(holder: PathDict, use_json: bool) -> None:
    """Print of directories in your PATH."""
    t = len(holder)
    e = sum([1 for d in holder.values() if not d.is_valid])
    d = sum([1 for d in holder.values() if holder.create_counter(d).is_duplicate])
    if use_json:
        info = dict(total=t, invalid=e, duplicates=d)
        print(json.dumps(info))
    else:
        print(t, "directories in your PATH")
        if e == 0:
            print("All directories exist")
        else:
            print(e, "do" if e > 1 else "does", "not exist")
        print(d, "duplicate" + "s" if d > 1 else "")
