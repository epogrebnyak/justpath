# pathit

Just let me see the PATH environment variable.

## Usage

| Question                         | Answer                    | Equivalent                                |
| -------------------------------- | ------------------------- | ----------------------------------------- |
| What direcotries are my PATH?    | `pathit`                  | `echo $PATH \| tr ";" "\n"`               |
| Sort them alphabetically!        | `pathit --sort`           | `echo $PATH \| tr ";" "\n" \| sort`       |
| What are the paths with `mingw`? | `pathit --includes mingw` | `echo $PATH \| tr ";" "\n" \| grep mingw` |

## Installation

```
git clone https://github.com/epogrebnyak/what-the-path.git
cd what-the-path
pip install -e .
```

or shorter:

```
pip install git+https://github.com/epogrebnyak/what-the-path.git
```

## Rationale

I'm scared of touching the PATH environment variable on my computer.
I do not understand which is a global PATH and which are user-defined PATHs and how they relate.
I do not understand why programs install so many of their directories into PATH and how to clean it. Even worse I hate it when I cannot easily check what the current PATH is,
so I wrote this small utility.

## Disclaimer

1. Better tools may exist.
2. `pathit` just shows the path and will not help you change it.

## Alternatives

bash commands are listed above. `pathit --sort` can be done as an inline command with Python:

```
python -c "import os; print('\n'.join(sorted(os.environ['PATH'].split(';'))))"
```
