# Exercise Index Setup Instructions

## Overview

This repository now includes an automated system to create a flat index of all exercises and code modules, making them easy to discover and access through your IDE or file explorer without changing the underlying chapter-based organization.

## What Was Added

1. **generate_symlinks.ps1** - PowerShell script that scans all chapter directories and creates symlinks
2. **create_symlinks.bat** - Windows batch file wrapper for easy double-click execution
3. **INDEX_README.md** - Complete documentation on using the index
4. **.gitignore** - Updated to exclude generated index directories

## Files Indexed

The system creates symlinks for:
- **Exercises**: `ex*.py` files from solutions/exercises/ch00-ch24/
- **Code Modules**: `ch*.py` files from course/code/ch00-ch27/
- **Solutions**: `sol_*.py` files from all chapter directories
- **Interludes**: `i_*.py` files if present
- **Tests**: `test_*.py` files from all code directories
- **Capstones**: Files from capstones directories

**Total**: 150+ indexed files

## Quick Setup (3 Steps)

### Option A: Double-Click Batch File (Easiest)

1. Navigate to the repository root: `D:\Learning\building-agents\building-agentic-ai\`
2. Double-click `create_symlinks.bat`
3. Watch the output and see your 150+ symlinks created

### Option B: PowerShell Command

Open PowerShell in the repository root and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "generate_symlinks.ps1" -Force
```

### Option C: From PowerShell ISE

```powershell
cd "D:\Learning\building-agents\building-agentic-ai"
.\generate_symlinks.ps1 -Force
```

## What Gets Created

After running the setup, you'll have:

```
solutions/exercises/_index/
├── ex0_4_basics.py              (exercise from ch00)
├── ex0_5_forecast.py            (exercise from ch00)
├── ex1_3_eli10.py               (exercise from ch01)
├── ex1_5_workflow.py            (exercise from ch01)
├── ... (all 50-70 exercises)
│
├── sol_ch02_calculator_agent.py (solution from ch00)
├── sol_ch03_tools.py            (solution from ch00)
├── ... (all 40-50 solutions)
└── (any interlude or test files)

course/code/_index/
├── ch00_http.py                 (code module from ch00)
├── ch00_json.py                 (code module from ch00)
├── ch01_routing.py              (code module from ch01)
├── ... (all 100+ code modules)
└── (any test files)
```

## Verify It Worked

After running the setup:

```powershell
# Check how many exercise symlinks were created
(ls solutions/exercises/_index/ | Measure-Object).Count

# Check how many code symlinks were created
(ls course/code/_index/ | Measure-Object).Count
```

Expected output:
- Exercises: ~90-120 files (exercises + solutions + interludes)
- Code: ~100-130 files (code modules + tests)

## Using the Index

### In VS Code
- Press `Ctrl+P`
- Type the exercise name: `ex1_5_workflow` → finds it in _index/
- Or search for a code module: `ch01_routing` → finds it in _index/

### In File Explorer
1. Navigate to `solutions/exercises/_index/` to see all exercises
2. Navigate to `course/code/_index/` to see all code modules
3. Click any file to open it (symlink follows the link automatically)

### In Terminal
```powershell
# Open an exercise directly
code solutions/exercises/_index/ex1_5_workflow.py

# Or inspect a code module
cat course/code/_index/ch00_http.py
```

## How Symlinks Work

- Symlinks are **shortcuts** that point to the actual files in chapter directories
- They're created using Windows `mklink` command
- Clicking them opens the **original file** - everything saves there
- They work with all IDEs, text editors, and command-line tools
- The original chapter structure remains completely unchanged

## Troubleshooting

### Problem: "Access Denied" error

This means you need administrator privileges. Right-click `create_symlinks.bat` and select "Run as administrator".

### Problem: Symlinks not showing in IDE

- Restart your IDE completely (close and reopen)
- Some IDEs cache the file structure on startup
- VS Code usually picks them up automatically

### Problem: Need to regenerate the index?

Just run the script again with `-Force` flag:
```powershell
.\generate_symlinks.ps1 -Force
```

This will recreate all symlinks without affecting the original files.

### Problem: Want to remove the index?

```powershell
Remove-Item solutions/exercises/_index -Recurse -Force
Remove-Item course/code/_index -Recurse -Force
```

The original chapter-based files are completely safe and unaffected.

## Technical Details

- **Symlink Type**: Windows NTFS junction links (not shortcuts)
- **Admin Privileges**: Usually not required; if needed, run as administrator
- **Compatibility**: Works with Python, IDEs, terminals, and file explorers
- **Git**: Index directories are in .gitignore - they're local-only and regenerated per developer
- **Portability**: Each developer regenerates their own index locally

## Next Steps

1. Run `create_symlinks.bat` to set up the index
2. Open VS Code and try searching for an exercise with Ctrl+P
3. Check `INDEX_README.md` for more detailed documentation
4. Start using the shorter paths to access your exercise files!

## Questions?

See `INDEX_README.md` for comprehensive documentation on:
- How the index works
- All file categories included
- Advanced customization
- Integration with development workflows

---

**Happy learning!**
