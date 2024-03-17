import os

def canonical(path):
    fs = [os.path.expandvars, os.path.expanduser, os.path.normcase]
    for f in fs:
        path = f(path)
    return path    


print(os.path.exists("~")) # False
print(os.path.exists(os.path.abspath("~"))) # False
print(os.path.exists(canonical("~"))) # True