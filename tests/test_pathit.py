import pytest
import subprocess
from pathit.show import typer_app
from typer.testing import CliRunner

runner = CliRunner()


def test_it_runs():
    result = runner.invoke(
        typer_app, ["show", "--sort", "--includes", "mingw", "--numbers"]
    )
    assert result.exit_code == 0


def test_it_runs_subprocess():
    args = ["pathit", "show", "--sort", "--includes", "mingw", "--numbers"]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
