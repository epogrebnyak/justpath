#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
	echo "Run this script, do not source it: ./readme.sh or bash readme.sh"
	return 1
fi

set -euo pipefail

# justpath invocation examples from README.md

justpath --raw
justpath
justpath --count
justpath --count --format json
justpath --invalid
justpath --duplicates
justpath --correct --format string
justpath --bare
justpath --includes bin
justpath --excludes windows
justpath --invalid
justpath --duplicates
justpath --purge-invalid --purge-duplicates
justpath --correct
justpath --correct --format string
justpath --sort 
justpath --sort --no-symlinks
justpath --sort --includes windows --excludes system32
justpath --sort --includes sdkman
justpath --includes quarto
justpath --includes quarto --invalid
justpath --includes quarto --correct

justpath --format json
justpath --correct --format string
justpath --count
justpath --count --format json
justpath --help
