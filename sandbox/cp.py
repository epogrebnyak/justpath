import subprocess

# Make subprocess.run() print a non-latin string on Windows

# https://www.reddit.com/r/learnpython/comments/1afcb97/how_to_make_subprocessrun_guess_the_enconding_of/
# https://github.com/python/cpython/issues/105312


# Run in console:
# set PYTHONIOENCODING=utf-8

result = subprocess.run(
    ["python", "-c", "print('Делавер')"],
    shell=True,
    capture_output=True,
    encoding="utf-8",
)
print(result.stdout)
print(result.stderr)
