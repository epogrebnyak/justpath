"""Explore PATH environment variable."""

import os
from dataclasses import dataclass


@dataclass
class Directory:
    raw: str
    canonical: str
    resolved: str  # resolve symlinks
    error: Exception | None

    @staticmethod
    def to_canonical(path: str) -> str:
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
        return self.error is None


def raw_path_var():
    return os.environ["PATH"]


@dataclass
class PathList:
    dirs: list[Directory]

    @classmethod
    def populate(cls):
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
        return self._count_duplicates(path, "raw")

    def count_resolved(self, path):
        return self._count_duplicates(path, "resolved")

    def counter(self, d):
        r1 = p.count_raws(d.raw)
        r2 = p.count_resolved(d.resolved)
        return Counter(r1, r2)

    def rjust(self, k: int):
        # number of digits in a line number, usually 1 or 2
        max_digits = len(str(len(self.dirs)))  # may simplify
        return str(k).rjust(max_digits)


@dataclass
class Counter:
    raw: int
    resolved: int

    @property
    def is_ok(self):
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
    dir: Directory
    counter: Counter

    @classmethod
    def new(cls, d: Directory, p: PathList):
        counter = p.counter(d)
        return cls(d, counter)

    def __bool__(self):
        return self.dir.is_valid and self.counter.is_ok

    def get_error_message(self) -> PathError | None:
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


p = PathList.populate()
for i, d in enumerate(p.dirs):
    lineno = p.rjust(i + 1)
    line = Line.new(d, p)
    if line:
        print(lineno, d.raw)
    else:
        err = line.get_error_message()
        print(lineno, "*", d.raw, err)
