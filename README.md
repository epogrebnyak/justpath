# pathit

Explore PATH environment variable on both Windows and Linux.

## Usage

What directories are part of PATH?

- `pathit show`
- or `echo $PATH | tr ";" "\n"` |

Sort them alphabetically:

- `pathit show --sort`
- or `echo $PATH | tr ";" "\n" | sort`

What are the paths with `bin`?

- `pathit show --includes bin`,
- or `echo $PATH | tr ";" "\n" | grep bin`

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

## Motivation

I'm scared of PATH environment variable syntax on Windows vs Linux,
so I wrote this small utility to be able to explore PATH more easily.

## Notes

1. Neither `pathit` nor any child process cannot modify your shell PATH, just view it.
2. Yes, you can run `echo $PATH | tr ";" "\n" | sort` instead of `pathit` on Linux.
3. Even better tools may exist:
   - [Rapid Environment Editor](https://www.rapidee.com/en/path-variable) for Windows is a gem (no affiliation, just a thankful user).
   - Maybe some smart command-line utility in Rust will emerge for PATH, but [not there yet](https://gist.github.com/sts10/).
