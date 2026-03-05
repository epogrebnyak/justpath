"""Explore PATH environment variable."""

from abc import ABC
import os
from dataclasses import dataclass
from collections import UserDict

from rich.console import Console
from rich.text import Text


PathErrorType = FileNotFoundError | NotADirectoryError | None


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
        """Create an instance from string."""
        visible_path = cls.to_canonical(raw)
        error: PathErrorType
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


def raw_path_var():
    """Return PATH environment variable."""
    try:
        return os.environ["PATH"]
    except KeyError:
        raise EnvironmentError("PATH variable not found")


class PathDict(UserDict[int, Directory]):
    """Represents directories from PATH."""

    @classmethod
    def populate(cls):
        """Create a PathDict by parsing the PATH environment variable."""
        paths = raw_path_var().split(os.pathsep)
        dirs = {i + 1: Directory.from_string(p) for i, p in enumerate(paths)}
        return cls(dirs)

    def filter_values(self, f) -> None:
        """Return a new PathDict with values filtered by a function."""
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

    def sorted(self) -> "PathDict":
        """Return a new PathDict sorted by validity and duplicates."""
        sorted_dirs = dict(
            sorted(self.items(), key=lambda x: (x[1].resolved, x[1].raw))
        )
        return PathDict(sorted_dirs)


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


# this is ABC class
class PathStatus(ABC):
    pass


class NoError(PathStatus):
    pass


@dataclass
class CriticalError(PathStatus):
    message: str


@dataclass
class MinorError(PathStatus):
    message: str


def get_color(status: PathStatus) -> str:
    """Return color based on error type."""
    match status:
        case CriticalError(_):
            return "red"
        case MinorError(_):
            return "gold3"
        case NoError():
            return "green"
        case _:
            raise ValueError("Unknown status type")


@dataclass
class PathItem:
    i: int
    dir: Directory
    duplicates: Counter

    def get_status(self) -> PathStatus:
        """Return an error message or no error for directory."""
        match self.dir.error:
            case FileNotFoundError():
                return CriticalError("directory does not exist")
            case NotADirectoryError():
                return CriticalError("not a directory")
            case None:
                if (n := self.duplicates.resolved) > 1:
                    return MinorError(f"{n} duplicates")
                else:
                    return NoError()
            # case _:
            #    return Minor("unknown error")


@dataclass
class SelectOptions:
    show_invalid: bool = False
    show_duplicates: bool = False
    sort: bool = False


text = Text()
text.append("Hello", style="green")
text.append(" World!", style="yellow")
text.append("Hello", style="grey74")
text.append(" World!", style="red")
console = Console()
console.print(text)


@dataclass
class DisplayOptions:
    show_line_numbers: bool = True
    follow_symlinks: bool = True
    show_errors: bool = True

    def apply(self, line: PathItem, max_digits: int) -> Text:
        """Format PathItem based on display options."""
        text = Text()
        if self.show_line_numbers:
            lineno = str(line.i).rjust(max_digits)
            text.append(lineno, style="grey74")
        status = line.get_status()
        style = get_color(status)
        text.append(" " + line.dir.raw, style=style)
        if self.follow_symlinks and line.dir.resolved != line.dir.raw:
            text.append(f" → {line.dir.resolved}", style="steel_blue1")
        if self.show_errors:
            match status:
                case CriticalError(message) | MinorError(message):
                    message = " (" + status.message + ")"
                    text.append(message, style="grey74")
                case _:
                    pass
        return text


def print_path(do: DisplayOptions, so: SelectOptions):
    """Print the directories in PATH with their validation status."""
    holder = PathDict.populate()
    if so.sort:
        holder = holder.sorted()

    def is_invalid(d: Directory) -> bool:
        return not d.is_valid

    def is_duplicate(d: Directory) -> bool:
        return not holder.create_counter(d).is_ok

    if so.show_invalid and so.show_duplicates:
        holder.filter_values(lambda d: is_invalid(d) or is_duplicate(d))
    if so.show_invalid:
        holder.filter_values(is_invalid)
    if so.show_duplicates:
        holder.filter_values(is_duplicate)
    max_digits = len(str(len(holder)))
    console = Console()
    for p in holder.path_items():
        message = do.apply(p, max_digits)
        console.print(message)


so = SelectOptions(show_invalid=False, show_duplicates=False, sort=True)
do = DisplayOptions()
print_path(do, so)
