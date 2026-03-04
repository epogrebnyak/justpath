"""Explore PATH environment variable."""

import os
from dataclasses import dataclass
from collections import UserDict


@dataclass
class Directory:
    """Represents a directory path."""

    raw: str
    canonical: str
    resolved: str  # resolve symlinks
    error: Exception | None

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
    """Represents a list of directories."""

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
        for i, d in self.items():
            counter = self.create_counter(d)
            yield PathItem(i, d, counter)

    def sorted(self) -> "PathDict":
        """Return a new PathDict sorted by validity and duplicates."""
        sorted_dirs = dict(sorted(self.items(), key=lambda x: x[1].raw))
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


@dataclass
class PathError:
    message: str


class Critical(PathError):
    pass


class Minor(PathError):
    pass


@dataclass
class PathItem:
    i: int
    dir: Directory
    duplicates: Counter

    def get_error_message(self) -> PathError | None:
        """Return an error message for directory."""
        match self.dir.error:
            case FileNotFoundError():
                return Critical("directory does not exist")
            case NotADirectoryError():
                return Critical("not a directory")
            case None:
                if (n := self.duplicates.resolved) > 1:
                    return Minor(f"{n} duplicates")
                else:
                    return None


@dataclass
class SelectOptions:
    show_invalid: bool = False
    show_duplicates: bool = False
    sort: bool = False


@dataclass
class DisplayOptions:
    show_line_numbers: bool = True
    follow_symlinks: bool = True
    show_errors: bool = True
    # color_output: bool = False

    def apply(self, line: PathItem, max_digits: int) -> str:
        """Format PathItem based on the display options."""
        parts = []
        if self.show_line_numbers:
            lineno = str(line.i).rjust(max_digits)
            parts.append(lineno)
        parts.append(line.dir.raw)
        if self.follow_symlinks and line.dir.resolved != line.dir.raw:
            parts.append(f"→ {line.dir.resolved}")
        if self.show_errors and (error := line.get_error_message()):
            parts.append("(" + error.message + ")")
        return " ".join(parts)


def print_path(do: DisplayOptions, so: SelectOptions):
    """Print the directories in PATH with their validation status."""
    holder = PathDict.populate()
    if so.sort:
        holder = holder.sorted()

    def is_error(x):
        return not x.is_valid

    def is_duplicate(x):
        return not holder.create_counter(x).is_ok

    if so.show_invalid and so.show_duplicates:
        holder.filter_values(lambda d: is_error(d) or is_duplicate(d))
    if so.show_invalid:
        holder.filter_values(is_error)
    if so.show_duplicates:
        holder.filter_values(is_duplicate)
    max_digits = len(str(len(holder)))
    for p in holder.path_items():
        message = do.apply(p, max_digits)
        print(message)


so = SelectOptions(show_invalid=False, show_duplicates=True, sort=True)
do = DisplayOptions()
print_path(do, so)
