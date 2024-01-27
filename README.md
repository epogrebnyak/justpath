# what-the-path

> Path it!

Just let me see my PATH environment variable in a readable way.

## Usage

| Question                             | Answer                    |
| ------------------------------------ | ------------------------- |
| What's on my PATH?                   | `pathit`                  |
| Sort this alphabetically!            | `pathit --sort`           |
| Who installed so many `mingw` paths? | `pathit --includes mingw` |

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

Obsously you can live without `pathit`:

| I type          | You type                                                                         |
| --------------- | -------------------------------------------------------------------------------- |
| `pathit`        | `echo $PATH \| tr ":" "\n"`                                                      |
| `pathit --sort` | `python -c "import os; print('\n'.join(sorted(os.environ['PATH'].split(';'))))"` |
