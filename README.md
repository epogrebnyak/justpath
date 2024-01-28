# justpath

Explore PATH environment variable on both Windows and Linux.

## Basic usage

What directories are part of PATH? Use `echo $PATH | tr ";" "\n"` or

```console
justpath show
```

Sort them alphabetically. Use `echo $PATH | tr ";" "\n" | sort` or

```console
justpath show --sort
```

What are the paths with `bin`? Use `echo $PATH | tr ";" "\n" | grep bin` or

```console
justpath show --includes bin
```

## Useful cases

More complex cases are easier with `justpath` than with bash on Linux or batch files in Windows.

### Directory does not exist

`justpath` will indicate if path does not exist or path is not a dicrectory.

Below is an example from Github Codespaces, somehow `/usr/local/sdkman/candidates/ant/current/bin` does not exist, but included in `PATH`.

```console
$ poetry run justpath show --sort --includes sdkman
19 /usr/local/sdkman/bin
23 /usr/local/sdkman/candidates/ant/current/bin (directory does not exist)
21 /usr/local/sdkman/candidates/gradle/current/bin
20 /usr/local/sdkman/candidates/java/current/bin
22 /usr/local/sdkman/candidates/maven/current/bin
```

### Filter directory names

`justpath` allows to filter paths that must or must not include a certain string.
Filtering is case insensitive, `--includes windows` and `--includes Windows` will
produce the same result.

```console
$ justpath show --sort --includes windows --excludes system32
39 C:\Users\Евгений\AppData\Local\Microsoft\WindowsApps
24 C:\WINDOWS
14 C:\Windows
46 C:\tools\Cmder\vendor\git-for-windows\cmd
47 C:\tools\Cmder\vendor\git-for-windows\mingw64\bin
12 C:\tools\Cmder\vendor\git-for-windows\usr\bin
```

### Purge invalid paths

`--purge` flag will drop invalid paths from listing.

```console
λ justpath show --includes quarto
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
50 x:\quarto\does_not_exist (directory does not exist)
51 d:\quarto\this_is_a_file (it's a file, not a directory)
```

```console
λ justpath show --includes quarto --purge
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
```

### Create a new content string for `PATH`

You can get a valid string for your PATH in a format native to your operating system
using `--string` ouput flag.

```console
λ justpath show --purge --string
C:\tools\Cmder\bin;C:\tools\Cmder\vendor\bin;C:\Windows\system32;C:\Windows
```

## Installation

### Stable version

```console
pip install justpath
```

### Development version

```console
git clone https://github.com/epogrebnyak/what-the-path.git
cd what-the-path
pip install -e .
```

or shorter:

```console
pip install git+https://github.com/epogrebnyak/what-the-path.git
```

## CLI tools

After installation you will get two aliases for the same command line tool:

```
pathit --help
justpath --help
```

## Motivation

PATH environment variable syntax on Windows vs Linux scares me,
so I wrote this utility to be able to explore PATH more easily.

## Notes

1. Neither `justpath` nor any child process cannot modify your shell PATH, just view it.
2. Yes, you can run `echo $PATH | tr ";" "\n" | sort` instead of `justpath show --sort` on Linux.
3. Even better tools than `justpath` may exist:
   - [Rapid Environment Editor](https://www.rapidee.com/en/path-variable) for Windows is a gem (no affiliation, just a thankful user).
   - Maybe some smart command-line utility in Rust will emerge for PATH, but [not there yet](https://gist.github.com/sts10/).
   - There is [pathdebug](https://github.com/d-led/pathdebug) written in Go that goes a step futher and attempts to trace where your PATH is defined.
