#!/usr/bin/env bash

set -euo pipefail

# justpath invocation examples from README.md

justpath --raw
justpath
justpath --count
justpath --invalid
justpath --duplicates
justpath --duplicates --follow-symlinks
justpath --correct --string

justpath --raw
justpath
justpath --bare
justpath --sort
justpath --includes bin
justpath --excludes windows
justpath --invalid
justpath --duplicates
justpath --purge-invalid --purge-duplicates
justpath --correct
justpath --correct --format string

justpath --sort --includes windows --excludes system32
justpath --sort --includes sdkman
justpath --includes quarto
justpath --includes quarto --invalid
justpath --includes quarto --correct

justpath --format json
justpath --correct --format string

justpath --count
justpath --count --json

justpath --help
