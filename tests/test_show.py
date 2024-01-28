import subprocess

from typer.testing import CliRunner

from justpath.show import typer_app

runner = CliRunner()


def test_it_runs():
    result = runner.invoke(
        typer_app, ["show", "--sort", "--includes", "mingw", "--display-numbers"]
    )
    assert result.exit_code == 0


def test_it_runs_subprocess():
    args = ["justpath", "show", "--sort", "--includes", "mingw", "--display-numbers"]
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0
