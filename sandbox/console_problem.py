# https://www.reddit.com/r/learnpython/comments/1afcb97/how_to_make_subprocessrun_guess_the_enconding_of/
# set PYTHONIOENCODING=utf-8
# python -c "import os; os.environ['STATE'] = 'Мэн'; print(os.environ['STATE'])"


import os
import subprocess

os.environ["STATE"] = "Делавер"

# This prints fine
t = os.environ["STATE"]
print("Printing non-latin env var from script works fine:")
print(t)

command = """
import os; os.environ['STATE'] = 'Мэн'; print(os.environ['STATE'])
"""
# import sys
# sys.stdout.reconfigure(encoding='utf-8')

print("\nAttempting to run subporcess:", command)

cmd = "; ".join(command.strip().split("\n"))
result = subprocess.run(
    ["python", "-c", cmd],
    # text=True,
    capture_output=True,
    # encoding="utf8"
)
print("\nResult (stdout):")
print(repr(result.stdout))

print("\nResult (stderr):")
print(result.stderr)

# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "d:\Anaconda3\lib\encodings\cp1252.py", line 19, in encode
#     return codecs.charmap_encode(input,self.errors,encoding_table)[0]
# UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-6: character maps to <undefined>

# Clues: https://stackoverflow.com/a/76776400/1758363
