import subprocess

import pytest
from typer.testing import CliRunner

from justpath.show import typer_app

commands = [
    ["--help"],
    ["stats"],
    ["show", "--errors"],
    ["show", "--sort", "--includes", "mingw", "--excludes", "tools", "--strip"],
    ["show", "--correct", "--string"],
]


@pytest.mark.parametrize(
    "args", commands + [["raw"]]
)  # raw give a fault with non-latin characters
def test_it_runs_with_cli_runner(args):
    runner = CliRunner()
    result = runner.invoke(typer_app, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("args", commands)
def test_it_runs_with_subprocess(args):
    args = ["justpath", *args]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
