# what-the-path

> Path it!

Just let me see my PATH environment variable in a readable way.

## Usage

You type `echo $PATH | tr \":\" \"\\n\"` I type:

```
pathit
```

You type `python -c "import os; print('\n'.join(sorted(os.environ['PATH'].split(';'))))"`
I type:

```
pathit --sort
```

## Installation

```
pip install pathit
```

## Rationale

I'm scared of touching the PATH environment variable on my computer.
I do not understand which is a global PATH and which are user-defined PATHs and how they relate.
I do not understand why programs install so many of their directories into PATH and how to clean it. Even worse I hate it when I cannot easily check what the current PATH is,
so I wrote this small utility.

## Disclaimer

1. Better tools may exist.
2. `pathit` just shows the path and will not help you change it.

## Examples

| Question                       | Answer                    |
| ------------------------------ | ------------------------- |
| What's on my PATH?             | `pathit`                  |
| Sort this alphabetically!      | `pathit --sort`           |
| Who installed so many `mingw`? | `pathit --includes mingw` |
