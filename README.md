# pathit

Explore PATH environment variable on both Windows and Linux.

## Usage

What directories are part of PATH?

`pathit show` or `echo $PATH | tr ";" "\n"`

Sort them alphabetically:

`pathit show --sort` or `echo $PATH | tr ";" "\n" | sort`

What are the paths with `bin`?

`pathit show --includes bin` or `echo $PATH | tr ";" "\n" | grep bin`

More complex sorting cases are easier with `pathit`.

`pathit` will indicate non-existent directory (this is an example from Github Codespaces,
somehow `/usr/local/sdkman/candidates/ant/current/bin` does not exist,
but included in `PATH`).

```console
$ poetry run pathit show --sort --includes sdkman
19 /usr/local/sdkman/bin
23 /usr/local/sdkman/candidates/ant/current/bin (directory does not exist)
21 /usr/local/sdkman/candidates/gradle/current/bin
20 /usr/local/sdkman/candidates/java/current/bin
22 /usr/local/sdkman/candidates/maven/current/bin
```

`pathit` allows to filter paths that must include or do not include a certain string.
Filtering is case insensitive, `--includes windows` and `--includes Windows` will
produce the same result.

```console
$ pathit show --sort --includes windows --excludes system32
39 C:\Users\Евгений\AppData\Local\Microsoft\WindowsApps
24 C:\WINDOWS
14 C:\Windows
46 C:\tools\Cmder\vendor\git-for-windows\cmd
47 C:\tools\Cmder\vendor\git-for-windows\mingw64\bin
12 C:\tools\Cmder\vendor\git-for-windows\usr\bin
```

`--purge` flag will drop invalid paths from listing.

```console
λ pathit show --includes quarto
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
50 x:\quarto\does_not_exist (directory does not exist)
51 d:\quarto\this_is_a_file (it's a file, not a directory)
```

```
λ pathit show --includes quarto --purge
33 C:\Program Files\Quarto\bin
41 D:\Quarto\bin
```

You can get a valid string for your PATH in native format using `--string`
ouput flag.

```
λ pathit show --purge --string
C:\tools\Cmder\bin;C:\tools\Cmder\vendor\bin;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0;C:\ProgramData\chocolatey\bin;C:\Program Files (x86)\Skype\Phone;C:\Program Files\Amazon\AWSCLI;C:\Program Files\Git\cmd;C:\WINDOWS\System32\OpenSSH;D:\Programs\Microsoft VS Code\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0;C:\WINDOWS\System32\OpenSSH
```

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

PATH environment variable syntax on Windows vs Linux scares me,
so I wrote this utility to be able to explore PATH more easily.

## Notes

1. Neither `pathit` nor any child process cannot modify your shell PATH, just view it.
2. Yes, you can run `echo $PATH | tr ";" "\n" | sort` instead of `pathit show --sort` on Linux.
3. Even better tools than `pathit` may exist:
   - [Rapid Environment Editor](https://www.rapidee.com/en/path-variable) for Windows is a gem (no affiliation, just a thankful user).
   - Maybe some smart command-line utility in Rust will emerge for PATH, but [not there yet](https://gist.github.com/sts10/).
   - There is [pathdebug](https://github.com/d-led/pathdebug) written in Go that goes a step futher and attempts to trace where your PATH is defined.
