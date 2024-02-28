import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from justpath.show import typer_app, PathVar


commands = [
    ["--help"],
    ["--raw"],
    ["--count"],
    ["--bare"],
    ["--sort", "--includes", "mingw", "--excludes", "tools"],
    ["--invalid"],
    ["--purge-invalid"],
    ["--duplicates"],
    ["--purge-duplicates"],
    ["--correct"],
]

# several commands give a fault with non-latin characters in subprocess call
# UnicodeEncodeError: 'charmap' codec can't encode characters in position \n894-900
# these commands are not tested with subprocess
more_commands = [["--raw"], ["--correct", "--string"]]


@pytest.mark.parametrize("args", commands + more_commands)
def test_it_runs_with_cli_runner(args):
    runner = CliRunner()
    result = runner.invoke(typer_app, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("args", commands)
def test_it_runs_with_subprocess(args):
    args = ["justpath", *args]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0


def test_from_list(tmp_path):
    pv = PathVar.from_list([tmp_path / "a", tmp_path / "b"])
    assert len(pv) == 2


def test_with_simlink_setup(tmp_path):
    a = tmp_path / "a"
    a.mkdir()
    b = Path(tmp_path / "b")
    b.symlink_to(a, target_is_directory=True)
    print(a.exists())
    print(b.exists())
    print(a)
    print(b)
    print(b.resolve())
    print(PathVar.from_list([a, b]).to_rows(True))
    assert True
