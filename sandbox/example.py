import subprocess

print(
    subprocess.run(
        ["python", "-c", "print('?')"],
        shell=True,
        encoding="utf-8",
        capture_output=True,
    ).stdout
)
