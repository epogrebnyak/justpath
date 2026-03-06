"""Explore PATH environment variable."""

import json
import os
from abc import ABC
from collections import UserDict
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.text import Text

PathErrorType = FileNotFoundError | NotADirectoryError | None


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
    error: PathErrorType

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
    def from_string(cls, raw: str):
        """Create a Directory instance from string."""
        visible_path = cls.to_canonical(raw)
        error: PathErrorType  # this is for mypy
        if not os.path.exists(visible_path):
            error = FileNotFoundError()
        elif not os.path.isdir(visible_path):
            error = NotADirectoryError()
        else:
            error = None
        return cls(raw, visible_path, os.path.realpath(visible_path), error)

    @property
    def is_valid(self) -> bool:
        """Check if the directory path exists and it is not a file."""
        return self.error is None
    
    def to_dict(self):
        """Return a dictionary representation of the Directory."""
        return {
            "raw": self.raw,
            "canonical": self.canonical,
            "resolved": self.resolved,
            "error": self.error_message,
        }
    
    @property
    def error_message(self) -> str:
        """Return a string representation of the error type."""
        match self.error:
            case FileNotFoundError():
                return "directory does not exist"
            case NotADirectoryError():
                return "not a directory"
            case None:
                return "none"
            case _:
                raise ValueError("Unknown error type")

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
    def populate(cls):
        """Create a PathDict by parsing the PATH environment variable."""
        paths = cls.raw().split(os.pathsep)
        dirs = {i + 1: Directory.from_string(p) for i, p in enumerate(paths)}
        return cls(dirs)

    def to_string(self):
        return os.pathsep.join(d.raw for d in self.values())

    def to_json(self):
        """Return JSON representation of PATH entries."""
        serial = {i: d.to_dict() for i, d in self.items()}
        return json.dumps(serial, indent=2)

    def filter_values(self, f) -> None:
        """Return a new PathDict with values filtered with f."""
        self.data = {k: v for k, v in self.items() if f(v)}

    def _count_duplicates(self, path: str, attr: str):
        return sum(1 for d in self.values() if getattr(d, attr) == path)

    def create_counter(self, d: Directory):
        """Return a Counter with raw and resolved path counts."""
        r1 = self._count_duplicates(d.raw, "raw")
        r2 = self._count_duplicates(d.resolved, "resolved")
        return Counter(r1, r2)

    def path_items(self):
        """Create a PathItem for a given directory."""
        for i, directory in self.items():
            counter = self.create_counter(directory)
            yield PathItem(i, directory, counter)

    def sort_resolved(self) -> "PathDict":
        """Sort inline by validity and duplicates."""
        self.data = dict(sorted(self.items(), key=lambda x: (x[1].resolved, x[1].raw)))

    def purge_invalid(self) -> "PathDict":
        """Purge invalid directories."""
        self.filter_values(lambda d: d.is_valid)

    def purge_duplicates(self) -> "PathDict":
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

        def is_invalid(d: Directory) -> bool:
            return not d.is_valid

        def is_duplicate(d: Directory) -> bool:
            return not self.create_counter(d).is_ok

        if so.sort:
            self.sort_resolved()
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
    def is_ok(self):
        """Check if the path appears exactly once in both raw and resolved forms."""
        return self.raw == 1 and self.resolved == 1

    @property
    def is_duplicate(self):
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
        match e := self.dir.error:
            case FileNotFoundError() | NotADirectoryError():
                return Error(Level.CRITICAL, self.dir.error_message)
            case None:
                if (n := self.duplicates.resolved) > 1:
                    return Error(Level.MINOR, f"{n} duplicates")
                else:
                    return NoError()


@dataclass
class ModifyOptions:
    purge_invalid: bool
    purge_duplicates: bool


@dataclass
class SelectOptions:
    show_invalid: bool
    show_duplicates: bool
    sort: bool


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
