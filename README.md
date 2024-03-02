# justpath

[![CI](https://github.com/epogrebnyak/justpath/actions/workflows/python-package.yml/badge.svg)](https://github.com/epogrebnyak/justpath/actions/workflows/python-package.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/justpath)](https://pypi.org/project/justpath/)

[reddit_shield]: https://img.shields.io/badge/Reddit-%23FF4500.svg?style=flat&logo=Reddit&logoColor=white
[hn_logo]: https://img.shields.io/badge/HackerNews-F0652F?logo=ycombinator&logoColor=white

Just a simple utility to explore `PATH` environment variable on both Windows and Linux.

## Workflow

`justpath` shows your `PATH` environment variable line by line with numbering, comments and highlighing
and helps detecting invalid or duplicate directories on your `PATH`.

You can also create a modified version of `PATH` string and use it to set `PATH` variable in your shell startup script or through an environment manager.
Note that `justpath` itself cannot change your shell `PATH`.

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

What are the paths that do not contain `windows` string?

```console
justpath --excludes windows
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
produce the same result. `--excludes` flag will filter out the directories containing provided string.

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

Use `--invalid` flag to explore what parts of PATH do not exist or not a directory.

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
flag. The duplicates are purged from the end of a string.

You may also add `--follow-symlinks` flag in order to resolve symbolic links
when counting and purging duplicate directories.

### 4. Dump `PATH` as JSON

`justpath` can dump a list of paths from `PATH` to JSON.
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

My own use case for `justpath` was exploring and sanitizing the `PATH` on Windows together with Rapid Environment Editor.
I also find it useful to inspect `PATH` on a remote enviroment like Codespaces to detect invalid paths.

## Feedback

Some of positive feedback I got about the `justpath` package:

> I like it! I do the steps involved in this occasionally, manually.
> It's not hard but this makes it nice.
> Not sure I'll use it since it is one more thing to install and remember,
> but the author had an itch and scratched it. Well done.

> It's handy to see your path entries in a list.
> Checking whether each entry is a valid location is neat, too.
> But even better, from my perspective, you published the code and got feedback from people,
> including related implementations. That’s worth it, in my book.
> Edit: I like the includes part, too.

> I think this is a cool package.
> Some of my first scripts in several languages have just been messing with file system abstractions.
> Files and file paths are much more complex than most people think.

## Discussions

[![Reddit][reddit_shield]](https://www.reddit.com/r/Python/comments/1aehs4i/clean_path_of_nonexistent_directories_with/)
[![Hacker News][hn_logo]](https://news.ycombinator.com/item?id=39493363)

I made posts about this package on Reddit and at Hacker News. Click on badges above to follow the discussions.

## Development notes

### More about `PATH`

See [links.md](docs/links.md) for more information about `PATH`.

### Making of command line interfaces (CLIs)

Few good links about CLI applications in general:

- [docopt](http://docopt.org/) is a great package to develop intuition about command line interfaces.
- [clig](https://clig.dev/) - ton of useful suggestions about CLIs including expected standard flags (`--silent`, `--json`, etc).
- [12 factor CLI app](https://panlw.github.io/15394417631263.html) - cited by `clig`.

## Alternatives

### Linux scripting

On Linux you can run `echo $PATH | tr ";" "\n"` to view your path line by line and
combine it with `grep`, `sort`, `uniq` and `wc -l` for the same effect
as most `justpath` commands.

The benefit of a script is that you do not need to install any extra dependency.
The drawback is that not everyone is good at writing bash scripts.
Scripting would also be a bit more problematic on Windows.

Check out the discussion at [Hacker News](https://news.ycombinator.com/item?id=39493363)
about bash and zsh scripts and `justpath` scenarios.

> [!TIP] > `--shell-equivalent` flag provides a reference about one line commands for several shells.
> Try `justpath --raw --shell-equivalent` or `justpath --shell-equivalent`.

### Other utilities

Even better tools than `justpath` may exist.

- [Rapid Environment Editor](https://www.rapidee.com/en/path-variable) for Windows
  is a gem (no affiliation).
- Maybe some smart command-line utility in Rust will emerge for PATH specifically,
  but [not there yet](https://gist.github.com/sts10/daadbc2f403bdffad1b6d33aff016c0a).
- There is [pathdebug](https://github.com/d-led/pathdebug) written in Go
  that goes a step futher and attempts to trace where your PATH is defined.
- There is a family of tools to manage environment paths
  like [dotenv](https://github.com/motdotla/dotenv) or its Python port, and a newer tool called [envio](https://github.com/envio-cli/envio) written in Rust.
