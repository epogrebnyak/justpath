#!/usr/bin/env python3
"""
Update the Homebrew formula with the latest version and dependencies.

This script:
1. Creates a clean virtual environment
2. Installs justpath and homebrew-pypi-poet
3. Generates resource stanzas using poet
4. Updates the Formula/justpath.rb file

Usage:
    python scripts/update_homebrew_formula.py

To also install/test locally:
    python scripts/update_homebrew_formula.py --test
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd: list[str], capture: bool = False) -> str | None:
    """Run a command and optionally capture output."""
    print(f"Running: {' '.join(cmd)}")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    subprocess.run(cmd, check=True)
    return None


def get_poet_output(venv_path: Path) -> str:
    """Get full formula from poet."""
    pip = venv_path / "bin" / "pip"
    poet = venv_path / "bin" / "poet"

    # Install justpath and poet
    run_cmd([str(pip), "install", "justpath", "homebrew-pypi-poet"])

    # Generate formula
    output = run_cmd([str(poet), "-f", "justpath"], capture=True)
    if output is None:
        raise RuntimeError("poet failed to generate output")

    return output


def parse_poet_formula(poet_output: str) -> dict:
    """Parse poet output and extract relevant parts."""
    result = {}

    # Extract URL
    url_match = re.search(r'url "(https://files\.pythonhosted\.org/[^"]+)"', poet_output)
    if url_match:
        result["url"] = url_match.group(1)

    # Extract sha256 (first occurrence is the main package)
    sha_match = re.search(r'sha256 "([a-f0-9]+)"', poet_output)
    if sha_match:
        result["sha256"] = sha_match.group(1)

    # Extract version from URL
    version_match = re.search(r'justpath-([0-9.]+)\.tar\.gz', poet_output)
    if version_match:
        result["version"] = version_match.group(1)

    # Extract all resource blocks
    resources = []
    resource_pattern = re.compile(
        r'resource "([^"]+)" do\n\s+url "([^"]+)"\n\s+sha256 "([^"]+)"\n\s+end',
        re.MULTILINE,
    )
    for match in resource_pattern.finditer(poet_output):
        name, url, sha = match.groups()
        # Skip types-colorama as it's only needed for type checking
        if "types-colorama" not in name:
            resources.append({"name": name, "url": url, "sha256": sha})

    result["resources"] = resources
    return result


def generate_formula(parsed: dict) -> str:
    """Generate the complete formula file."""
    resources_str = "\n\n".join(
        f'''  resource "{r['name']}" do
    url "{r['url']}"
    sha256 "{r['sha256']}"
  end'''
        for r in parsed["resources"]
    )

    formula = f'''class Justpath < Formula
  include Language::Python::Virtualenv

  desc "Explore PATH environment variable on Windows and Linux"
  homepage "https://github.com/epogrebnyak/justpath"
  url "{parsed['url']}"
  sha256 "{parsed['sha256']}"
  license "GPL-3.0-or-later"

  depends_on "python@3.12"

{resources_str}

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test that the command runs and shows help
    assert_match "Show directories from PATH", shell_output("#{{bin}}/justpath --help")

    # Test that it can count paths (output will vary but should not error)
    assert_match "directories in your PATH", shell_output("#{{bin}}/justpath --count")
  end
end
'''
    return formula


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Homebrew formula")
    parser.add_argument("--test", action="store_true", help="Run brew test after updating")
    args = parser.parse_args()

    # Find paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    formula_path = repo_root / "Formula" / "justpath.rb"

    # Create temp venv
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = Path(tmpdir) / "venv"
        run_cmd([sys.executable, "-m", "venv", str(venv_path)])

        # Get poet output
        poet_output = get_poet_output(venv_path)

        # Parse and generate
        parsed = parse_poet_formula(poet_output)
        formula_content = generate_formula(parsed)

        # Write formula
        formula_path.write_text(formula_content)
        print(f"Updated {formula_path}")
        print(f"  Version: {parsed['version']}")
        print(f"  SHA256: {parsed['sha256']}")
        print(f"  Resources: {len(parsed['resources'])}")

    if args.test:
        print("\nRunning brew test...")
        # Copy to tap if it exists
        tap_formula = Path("/opt/homebrew/Library/Taps/eturino/homebrew-justpath/Formula/justpath.rb")
        if tap_formula.parent.exists():
            shutil.copy(formula_path, tap_formula)
            run_cmd(["brew", "reinstall", "eturino/justpath/justpath", "--build-from-source"])
            run_cmd(["brew", "test", "eturino/justpath/justpath"])
        else:
            print("Tap not found, skipping test")

    return 0


if __name__ == "__main__":
    sys.exit(main())
