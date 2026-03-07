# PATH One-Liners


This documentation covers common tasks for PATH inspection and manipulation, with equivalent shell commands across multiple platforms:
- **bash** (Linux/macOS)
- **cmd.exe** (Windows)
- **PowerShell** (Windows)
- **Python** (cross-platform)
- **justpath** (cross-platform)


## Commands

### 1. Print PATH as is

**Task:** Display the raw PATH environment variable without any modifications.

#### Bash (Linux/macOS)
```bash
echo $PATH
```

#### cmd.exe (Windows)
```cmd
echo %PATH%
```

#### PowerShell (Windows)
```powershell
echo $Env:PATH
```

#### Python (any OS)
```python
import os; print(os.environ['PATH'])
```

#### justpath (any OS)
```bash
justpath --raw
```

**Description:** This shows the PATH variable exactly as it is stored, with directory paths separated by the OS-specific path separator (`:` on Unix-like systems, `;` on Windows).

---

### 2. Print PATH by line

**Task:** Display each PATH directory on a separate line, making it easier to read and analyze.

#### Bash (Linux/macOS)
```bash
echo $PATH | tr ":" "\n" | nl
```

**Breakdown:**
- `echo $PATH` - Output the PATH variable
- `tr ":" "\n"` - Translate colons to newlines (splits by path separator)
- `nl` - Add line numbers to each directory

#### PowerShell (Windows)
```powershell
$env:PATH.split(";")
```

**Breakdown:**
- `$env:PATH` - Access the PATH environment variable
- `.split(";")` - Split on semicolon (Windows path separator)

#### Python (any OS)
```python
import os; print(os.environ['PATH'].replace(os.pathsep, '\n'))
```

**Breakdown:**
- `os.environ['PATH']` - Get the PATH variable
- `.replace(os.pathsep, '\n')` - Replace the OS-specific separator with newlines

#### justpath
```bash
justpath
```

**Description:** Line-by-line display is useful for reading PATH entries, finding specific directories, and identifying duplicates or invalid paths. Add `nl` in bash to get line numbers like justpath does by default.

---

### 3. Show duplicate directories

**Task:** Identify directories that appear more than once in the PATH.

#### Bash (Linux/macOS) - Note: Order may not be preserved
```bash
echo $PATH | tr ":" "\n" | sort | uniq -d
```

**Breakdown:**
- `echo $PATH` - Output the PATH variable
- `tr ":" "\n"` - Split on colons to get one directory per line
- `sort` - Sort the directories (this changes the original order)
- `uniq -d` - Print only duplicate lines

**Caveat:** This approach sorts the directories, which changes the order they appeared in the original PATH.

#### justpath - Preserves order from PATH
```bash
justpath --duplicates
```

**Description:** Duplicates occur when the same directory is listed multiple times in PATH, which wastes resources and can cause confusion. The bash approach finds duplicates but loses order, while justpath shows duplicates while preserving their original positions in PATH.

---

## Key Differences by Platform

| Feature | Bash | cmd.exe | PowerShell | Python | justpath |
|---------|------|---------|------------|--------|----------|
| Path separator in PATH | `:` | `;` | `;` | `os.pathsep` | Auto-detected |
| Preserves order | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shows line numbers | With `nl` | ✗ | ✗ | ✗ | ✓ |
| Validates paths | ✗ | ✗ | ✗ | ✗ | ✓ |
| Shows symlink targets | ✗ | ✗ | ✗ | ✗ | ✓ |
| Cross-platform | ✗ | Windows only | Windows only | ✓ | ✓ |
