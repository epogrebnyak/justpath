# what-the-path

> Path it!

Just let me see my PATH environment variable in a readable way.

## Usage

Instead of `echo $PATH | tr \":\" \"\\n\"` I type:

```
pathit
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
