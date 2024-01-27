import pytest
import subprocess
from pathit.show import typer_app
from typer.testing import CliRunner

runner = CliRunner()

# do not know how to make a Typer app with no subcommands
@pytest.mark.skip
def test_it_runs():
    result = runner.invoke(typer_app, ["--sort", "--includes", "mingw"])
    assert result.exit_code == 0


def test_it_runs_subprocess():
    # must have package script installed with `pip install -e .`
    args = ["pathit", "--sort", "--includes", "mingw"]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
