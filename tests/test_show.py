import subprocess

import pytest
from typer.testing import CliRunner

from justpath.show import typer_app

commands = [
    ["--help"],
    ["count"],
    ["count", "--json"],
    ["show", "--errors"],
    ["show", "--sort", "--includes", "mingw", "--excludes", "tools", "--strip"],
]

# several commands give a fault with non-latin characters in subprocess call
# UnicodeEncodeError: 'charmap' codec can't encode characters in position \n894-900
# these commands are not tested with subprocess
more_commands = [["raw"], ["lines"], ["show", "--correct", "--string"]]


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
