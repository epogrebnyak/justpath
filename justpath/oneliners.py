from dataclasses import dataclass


@dataclass
class OneLiner:
    job: str
    justpath_args: str
    bash: str = ""
    cmd: str = ""
    ps: str = ""
    python: str = ""

    @property
    def justpath(self):
        return "justpath " + self.justpath_args

    @property
    def python_command(self):
        return f'python -c "{self.python}"'

    def print(self):
        print(self.job)
        if self.bash:
            print("bash (Linux):\n ", self.bash)
        if self.cmd:
            print("cmd.exe (Windows):\n ", self.cmd)
        if self.ps:
            print("poweshell (Windows):\n ", self.ps)
        if self.python:
            print("python (any OS):\n ", self.python_command)
        print("justpath (any OS):\n ", self.justpath)


RAW = OneLiner(
    job="Print PATH as is",
    justpath_args="--raw",
    bash="echo $PATH",
    cmd="echo %PATH%",
    ps="echo $Env:PATH",
    python="import os; print(os.environ['PATH']",
)

BY_LINE = OneLiner(
    job="Print PATH by line (possibly with line numbers)",
    justpath_args="",
    bash='echo $PATH |  tr ":" "\\n" | nl',
    ps='$env:PATH.split(";")',
    python="import os; print(os.environ['PATH'].replace(os.pathsep, '\\n'))",
)

DUPLICATES = OneLiner(
    job="Show duplicate directories",
    justpath_args="--duplicates                        # preserves order from PATH",
    bash='echo $PATH |  tr ":" "\\n" | sort | uniq -d   # does not preserve order from PATH',
)


def print_alternatives():
    for job in [RAW, DUPLICATES, BY_LINE]:
        job.print()
        print()
