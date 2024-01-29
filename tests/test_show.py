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
    ["show", "--correct", "--string"],
]

# raw command gives a fault with non-latin characters in subprocess call
more_commands = [["raw"]]

@pytest.mark.parametrize(
    "args", commands + more_commands
)  
def test_it_runs_with_cli_runner(args):
    runner = CliRunner()
    result = runner.invoke(typer_app, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("args", commands)
def test_it_runs_with_subprocess(args):
    args = ["justpath", *args]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
