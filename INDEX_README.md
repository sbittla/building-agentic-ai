# Exercise and Code Index

This document explains the flat index structure that provides direct access to all exercises and code modules while maintaining the chapter-based folder organization.

## Quick Start

To set up the index structure with symlinks:

1. On Windows, run from the repository root:
   ```bash
   create_symlinks.bat
   ```

   Or run directly in PowerShell:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "generate_symlinks.ps1" -Force
   ```

## Directory Structure

The index creates two flat directories with symlinks:

### Exercises Index
```
solutions/exercises/_index/
├── ex0_4_basics.py         → ../ch00/ex0_4_basics.py
├── ex0_5_forecast.py       → ../ch00/ex0_5_forecast.py
├── ex0_6_city_temperature.py → ../ch00/ex0_6_city_temperature.py
├── ex1_3_eli10.py          → ../ch01/ex1_3_eli10.py
├── ex1_5_workflow.py       → ../ch01/ex1_5_workflow.py
├── ... (all exercise files)
├── sol_ch02_calculator_agent.py → ../ch00/sol_ch02_calculator_agent.py
├── sol_ch03_tools.py       → ../ch00/sol_ch03_tools.py
├── ... (all solution files)
├── i_*.py                  → (all interlude files if present)
└── test_*.py               → (all test files if present)
```

### Code Modules Index
```
course/code/_index/
├── ch00_http.py            → ../ch00/ch00_http.py
├── ch00_json.py            → ../ch00/ch00_json.py
├── ch00_python_tour.py     → ../ch00/ch00_python_tour.py
├── ch01_*.py               → ../ch01/ch01_*.py
├── ... (all code module files)
├── test_*.py               → (all test files from code directories)
└── capstone_*.py           → ../capstones/capstone_*.py
```

## What This Enables

✅ **Direct File Discovery**: Access `_index/ex1_5_workflow.py` instead of navigating to `ch01/ex1_5_workflow.py`

✅ **IDE Integration**: Your IDE's file explorer and search show both the chapter structure and the flat index

✅ **Quick Access**: Terminal completion and file search work with shorter paths

✅ **File Search**: Use Ctrl+P (VS Code) or Cmd+P (most IDEs) to quickly find any exercise or module by name

✅ **Backward Compatible**: All original chapter-based paths continue to work; nothing is moved or renamed

## File Categories

The index includes:

1. **Exercises** (`ex*.py`): Main exercise files you need to complete
2. **Solutions** (`sol_*.py`): Complete solutions for reference
3. **Interludes** (`i_*.py`): Supporting code snippets and examples
4. **Code Modules** (`ch##_*.py`): Reusable code modules and utilities
5. **Tests** (`test_*.py`): Test files for code modules

## How Symlinks Work

Windows symlinks (created with `mklink` command):
- Point to the original files in chapter directories
- Require no admin privileges on NTFS drives (in most cases)
- Show up as file shortcuts in Windows Explorer
- Work with all IDEs and command-line tools
- Can be refreshed anytime by re-running the batch file with `-Force` flag

## Troubleshooting

### "Access Denied" when creating symlinks
This typically means:
- You need to run the batch file as Administrator, OR
- Your Windows system has symlink creation disabled

**Solution**: Right-click `create_symlinks.bat` → "Run as administrator"

### Symlinks not working in your IDE
- Ensure your IDE is restarted after creating symlinks
- Some IDEs cache the file structure on startup
- VS Code usually picks up new symlinks automatically

### Need to recreate the index?
```powershell
# This will recreate all symlinks, replacing existing ones
powershell -NoProfile -ExecutionPolicy Bypass -File "generate_symlinks.ps1" -Force
```

## Index Statistics

| Category | Count |
|----------|-------|
| Exercise Files | ~50-70 |
| Code Modules | ~100+ |
| Solution Files | ~40-50 |
| Test Files | Variable |
| **Total Symlinks** | **150+** |

## Verification

To verify the index was created correctly:

```powershell
# Check exercise index
ls solutions/exercises/_index/ | Measure-Object -Line

# Check code index
ls course/code/_index/ | Measure-Object -Line
```

## Integration with Git

The `_index` directories are already in `.gitignore` (symlinks are not tracked). You only need to track:
- `generate_symlinks.ps1` - The script to create symlinks
- `create_symlinks.bat` - The batch file wrapper
- `INDEX_README.md` - This documentation

This allows every developer to quickly regenerate their local index.

## Manual Cleanup

To remove the index structure:

```powershell
# Remove all symlinks (preserves the original files)
Remove-Item solutions/exercises/_index -Recurse -Force
Remove-Item course/code/_index -Recurse -Force

# Or just delete the directories manually
```

The original chapter-based structure remains completely intact.
