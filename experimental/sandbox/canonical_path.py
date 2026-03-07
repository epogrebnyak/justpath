import os


def canonical(path):
    fs = [
        os.path.expandvars,  # expands variables like %name% or $NAME, perhaps rare on PATH
        os.path.expanduser,  # expands ~, shell-dependent
        os.path.normcase,  # to lowercase, to make prettier
    ]
    for f in fs:
        path = f(path)
    return path


print(os.path.exists("~"))  # False
print(os.path.exists(os.path.abspath("~")))  # False
print(os.path.exists(canonical("~")))  # True
print(os.path.isdir("~"))  # False
print(os.path.isdir(canonical("~")))  # True
