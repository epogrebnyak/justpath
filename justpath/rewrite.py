"""Explore PATH environment variable."""

import os
from dataclasses import dataclass


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


@dataclass
class PathList:
    """Represents a list of directories."""

    dirs: list[Directory]

    @classmethod
    def populate(cls):
        """Create a PathList by parsing the PATH environment variable."""
        paths = raw_path_var().split(os.pathsep)
        dirs = [Directory.from_string(p) for p in paths]
        return cls(dirs)

    def _count_duplicates(self, path: str, attr: str):
        count = 0
        for d in self.dirs:
            if getattr(d, attr) == path:
                count += 1
        return count

    def count_raws(self, path):
        """Count how many directories have the same raw path."""
        return self._count_duplicates(path, "raw")

    def count_resolved(self, path):
        """Count how many directories have the same resolved path."""
        return self._count_duplicates(path, "resolved")

    def counter(self, d: Directory):
        """Return a Counter with raw and resolved path counts."""
        r1 = self.count_raws(d.raw)
        r2 = self.count_resolved(d.resolved)
        return Counter(r1, r2)

    def rjust(self, k: int):
        """Right-justify a line number based on the total number of directories."""
        # number of digits in a line number, usually 1 or 2
        max_digits = len(str(len(self.dirs)))
        return str(k).rjust(max_digits)


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

    def __str__(self):
        return "(" + self.message + ")"


class Critical(PathError):
    pass


class Minor(PathError):
    pass


@dataclass
class Line:
    """Represents a line of output showing a directory and its validation status."""

    dir: Directory
    counter: Counter

    @classmethod
    def new(cls, d: Directory, p: PathList):
        """Create a new Line instance for a directory with its counter."""
        counter = p.counter(d)
        return cls(d, counter)

    def __bool__(self):
        """Return True if the directory is valid and has no duplicates."""
        return self.dir.is_valid and self.counter.is_ok

    def get_error_message(self) -> PathError | None:
        """Return an error message for directory."""
        match self.dir.error:
            case FileNotFoundError():
                return Critical("directory does not exist")
            case NotADirectoryError():
                return Critical("not a directory")
            case None:
                if (n := self.counter.resolved) > 1:
                    return Minor(f"found {n} duplicates")
                else:
                    return None


def print_path(line_numbers: bool = True):
    """Print the directories in PATH with their validation status."""
    p = PathList.populate()
    for i, d in enumerate(p.dirs):
        print_items = []
        if line_numbers:
            print_items.append(p.rjust(i + 1))
        line = Line.new(d, p)
        if line:
            print_items.append(d.raw)
        else:
            err = line.get_error_message()
            print_items.extend(["*", d.raw, str(err)])
        print(" ".join(print_items))


print_path(False)
