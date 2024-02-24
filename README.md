# justpath

[![Reddit](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=flat&logo=Reddit&logoColor=white)][reddit]
[![PyPI - Version](https://img.shields.io/pypi/v/justpath)](https://pypi.org/project/justpath/)
[![CI](https://github.com/epogrebnyak/justpath/actions/workflows/python-package.yml/badge.svg)](https://github.com/epogrebnyak/justpath/actions/workflows/python-package.yml)

[reddit]: https://www.reddit.com/r/Python/comments/1aehs4i/clean_path_of_nonexistent_directories_with/

Just a simple utility to explore `PATH` environment variable on both Windows and Linux.

## Workflow

Note that neither `justpath` nor any child process cannot modify your shell `PATH`, you can just view it.

With `justpath` you can get a modified version of `PATH` (e.g. by excluding non-existent directory),
and later use this new string to set `PATH` in your shell startup script or with an environment manager.

## Try quickly

Install:

```
pip install justpath
```

Try the following:

```console
justpath --raw
justpath
justpath --count
justpath --invalid
justpath --duplicates
justpath --correct --string
```
## Screencast

[![asciicast](https://asciinema.org/a/RjfqfUhcI4iJKNw55sSkuioU5.svg)](https://asciinema.org/a/RjfqfUhcI4iJKNw55sSkuioU5)

## Basic usage

What is the raw content of `PATH` string?

```console
justpath --raw
```

List directories in `PATH` line by line.

```console
justpath
```

Same as above, but no line numbers, no comments, no color, just bare text.

```console
justpath --bare --no-color
```

Show directories from PATH in alphabetic order[^1]:

```console
justpath --sort
```

[^1]: Sorting helps to view and analyze `PATH`. Do not put a sorted `PATH` back on your system as you will loose useful information about path resolution order.

What are the paths that contain `bin` string?

```console
justpath --includes bin
```

Are there any directories in `PATH` that do not exist?

```console
justpath --invalid
```

Are there any duplicate directories in `PATH`?

```console
justpath --duplicates
```

What is the `PATH` without invalid paths and duplicates?

```console
justpath --purge-invalid --purge-duplicates
```

More concise:

```console
justpath --correct
```

A clean `PATH` string in OS-native format:

```console
justpath --correct --string
```

## Useful cases

### 1. Filter directory names

`justpath` allows to filter paths that must or must not include a certain string.
Filtering is case insensitive, `--includes windows` and `--includes Windows` will
produce the same result.

```console
λ justpath --sort --includes windows --excludes system32
39 C:\Users\Евгений\AppData\Local\Microsoft\WindowsApps
24 C:\WINDOWS
14 C:\Windows
46 C:\tools\Cmder\vendor\git-for-windows\cmd
47 C:\tools\Cmder\vendor\git-for-windows\mingw64\bin
12 C:\tools\Cmder\vendor\git-for-windows\usr\bin
```

### 2. Directory does not exist or not a directory

`justpath` will indicate if path does not exist or path is not a directory.

Below is an example from Github Codespaces, for some reason
`/usr/local/sdkman/candidates/ant/current/bin` does not exist,
but included in `PATH`.

```console
λ justpath --sort --includes sdkman
19 /usr/local/sdkman/bin
23 /usr/local/sdkman/candidates/ant/current/bin (directory does not exist)
21 /usr/local/sdkman/candidates/gradle/current/bin
20 /usr/local/sdkman/candidates/java/current/bin
22 /usr/local/sdkman/candidates/maven/current/bin
```

Added file `touch d:\quarto\this_is_a_file` for example below.

```console
λ justpath --includes quarto
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
50 x:\quarto\does_not_exist (directory does not exist)
51 d:\quarto\this_is_a_file (not a directory)
```

Use `--invalid` flag to explore what is parts of PATH do not exist.

```console
λ justpath --includes quarto --invalid
50 x:\quarto\does_not_exist (directory does not exist)
51 d:\quarto\this_is_a_file (not a directory)
```

### 3. Purge incorrect paths

`--correct` flag will drop invalid paths from listing.

```console
λ justpath --includes quarto --correct
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
```

`--correct` flag is the same as applying both `--purge-invalid` and `--purge-duplicates`
flag.

### 4. Dump `PATH` as JSON

`justpath` you can dump a list of paths from `PATH` to JSON.
You may add `--correct` flag to list only correct paths.

```
justpath --correct --json
```

### 5. Create new content string for `PATH`

With `justpath` you can create new `PATH` contents and use it in your shell startup script.
As any child process `justpath` itself cannot modify PATH in your current environment.

You can get a valid string for your PATH in a format native to your operating system
using `--string` ouput flag.

```console
λ justpath --correct --string
C:\tools\Cmder\bin;C:\tools\Cmder\vendor\bin;C:\Windows\system32;C:\Windows;...
```

### 6. Count directories in `PATH`

```console
λ justpath --count
52 directories in your PATH
1 does not exist
16 duplicates
```

```
λ justpath --count --json
{"total": 52, "invalid": 1, "duplicates": 16}
```

## Installation

### Stable version

```console
pip install justpath
```

### Development version

```console
git clone https://github.com/epogrebnyak/justpath.git
cd justpath
pip install -e .
```

or shorter:

```console
pip install git+https://github.com/epogrebnyak/justpath.git
```

## CLI tool

After installation you can try the command line script:

```
justpath --help
```

## Motivation

I think [this quote][quote] about `PATH` is quite right:

> I always get the feeling that nobody knows what a PATH is and at this point they are too afraid to ask.

[quote]: https://www.reddit.com/r/linuxquestions/comments/pgv7hm/comment/hbf3bno/

`PATH` environment variable syntax on Windows and on Linux are different,
so I wrote this utility to be able to explore `PATH` more easily.

## Development notes

- See [links.md](docs/links.md) for more about `PATH`.
- Few good links about CLI apps in general
  - [docopt](http://docopt.org/) is a great package to develop intuition about command line interfaces.
  - [clig](https://clig.dev/) - ton of useful suggestions about CLIs.
  - [12 factor CLI app](https://panlw.github.io/15394417631263.html) - cited by `clig`.

## Alternatives

Even better tools than `justpath` may exist.

- On Linux you can run `echo $PATH | tr ";" "\n"` to view your path line by line and
  combine it with `grep` to gain more insights.
- [Rapid Environment Editor](https://www.rapidee.com/en/path-variable) for Windows
  is a gem (no affiliation).
- Maybe some smart command-line utility in Rust will emerge for PATH specifically,
  but [not there yet](https://gist.github.com/sts10/daadbc2f403bdffad1b6d33aff016c0a).
- There is [pathdebug](https://github.com/d-led/pathdebug) written in Go
  that goes a step futher and attempts to trace where your PATH is defined.
- There is a family of tools to manage environment paths on like [dotenv](https://github.com/motdotla/dotenv)
  or its Python port, and a newer tool called [envio](https://github.com/envio-cli/envio) written in Rust.
