# Make subprocess.run() print a non-latin string on Windows

# Running this code via subprocess.run() results in `UnicodeEncodeError`
# on Windows:

import subprocess
result = subprocess.run(
    ["python", "-c", "print('Делавер')"],
    text=True,
    capture_output=True,
)
print(result.stdout)
print(result.stderr)

# Changing `text=True` to `encoding="utf8"` does not help.

# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "D:\Anaconda3\lib\encodings\cp1252.py", line 19, in encode
#     return codecs.charmap_encode(input,self.errors,encoding_table)[0]
# UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-6: character maps to <undefined>
