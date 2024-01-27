# pathit

Just let me see the PATH environment variable on both Windows and Linux.

## Usage

| Question                         | Answer                         | Equivalent                                |
| -------------------------------- | ------------------------------ | ----------------------------------------- |
| What direcotries are my PATH?    | `pathit show`                  | `echo $PATH \| tr ";" "\n"`               |
| Sort them alphabetically!        | `pathit show --sort`           | `echo $PATH \| tr ";" "\n" \| sort`       |
| What are the paths with `mingw`? | `pathit show --includes mingw` | `echo $PATH \| tr ";" "\n" \| grep mingw` |

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

I'm scared of PATH environment variable syntax on Windows vs Linux,
so I wrote this small utility to be able to explore the path more easily.

## Disclaimer

1. Yes, you can run `echo $PATH | tr ";" "\n" | sort` and even better tools may exist.
2. `pathit` or any child process cannot modify PATH, but it can provide a command to do so.
