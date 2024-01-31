import ctypes
import subprocess

# # Get the console's active code page, as an integer.
# oemCP = ctypes.windll.kernel32.GetConsoleOutputCP()
# encoding = "cp" + str(oemCP)

# process = subprocess.run("python -c \"import chardet; print(chardet.detect('Я'.encode('cp1251')))\"", capture_output=True)

# # Decode based on the console's active code page.
# print(process.stdout.decode(encoding))
# print(process.stderr)

# Make subprocess.run() print a non-latin string on Windows

# Running this code via subprocess.run() results in `UnicodeEncodeError`
# on Windows:

# https://github.com/python/cpython/issues/105312


# result = subprocess.run(
#     ["python", "-c", "print('Делавер')"],
#     capture_output=True,
#     encoding="utf8",
# )
# print(result.stdout)
# print(result.stderr)

import subprocess
print(subprocess.run(["python", "-c", "print('Я')"], shell=True, text=True, capture_output=True).stderr)

# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "d:\Anaconda3\lib\encodings\cp1252.py", line 19, in encode
#     return codecs.charmap_encode(input,self.errors,encoding_table)[0]
# UnicodeEncodeError: 'charmap' codec can't encode character '\u042f' in position 0: character maps to <undefined


# Changing `text=True` to `encoding="utf8"` does not help.

# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "D:\Anaconda3\lib\encodings\cp1252.py", line 19, in encode
#     return codecs.charmap_encode(input,self.errors,encoding_table)[0]
# UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-6: character maps to <undefined>
