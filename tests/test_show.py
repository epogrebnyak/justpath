import pytest

import subprocess

from typer.testing import CliRunner

from justpath.show import typer_app


commands = [
   ["--help"],
   ["show", "--sort", "--includes", "mingw", "--display-numbers"]
]

@pytest.mark.parametrize("args", commands)
def test_it_runs_with_cli_runner(args):
    runner = CliRunner()
    result = runner.invoke(
        typer_app, args
    )
    assert result.exit_code == 0

@pytest.mark.parametrize("args", commands)
def test_it_runs_with_subprocess(args):
    args = ["justpath", *args]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
