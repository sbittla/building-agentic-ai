# PowerShell script to create symlinks for Building Agentic AI course files
# This script creates a flat index structure with symlinks for easy file discovery

param(
    [string]$BasePath = "D:\Learning\building-agents\building-agentic-ai",
    [switch]$Force
)

# Track results
$results = @{
    exerciseSymlinks = @()
    codeSymlinks = @()
    solutionSymlinks = @()
    interludes = @()
    tests = @()
    errors = @()
}

# Create directories if they don't exist
$exerciseIndexPath = "$BasePath\solutions\exercises\_index"
$codeIndexPath = "$BasePath\course\code\_index"

Write-Host "Creating index directories..." -ForegroundColor Cyan
if (-not (Test-Path $exerciseIndexPath)) {
    New-Item -ItemType Directory -Path $exerciseIndexPath -Force | Out-Null
    Write-Host "Created: $exerciseIndexPath"
}

if (-not (Test-Path $codeIndexPath)) {
    New-Item -ItemType Directory -Path $codeIndexPath -Force | Out-Null
    Write-Host "Created: $codeIndexPath"
}

# Get all exercise files
Write-Host "`nScanning exercise directories..." -ForegroundColor Cyan
$exercisesPath = "$BasePath\solutions\exercises"
$chapterDirs = Get-ChildItem -Path $exercisesPath -Directory | Where-Object { $_.Name -match '^ch\d{2}$|^capstones$' }

foreach ($chapterDir in $chapterDirs) {
    $chapterPath = $chapterDir.FullName
    $chapterName = $chapterDir.Name
    
    # Get exercise files (ex*.py)
    $exerciseFiles = Get-ChildItem -Path $chapterPath -Filter "ex*.py" -File
    foreach ($file in $exerciseFiles) {
        $fileName = $file.Name -replace '\.py$'
        $targetPath = Join-Path $exerciseIndexPath ($fileName + ".py")
        $sourcePath = "..\$chapterName\$($file.Name)"
        
        if (Test-Path $targetPath) {
            if (-not $Force) {
                $results.errors += "Symlink already exists: $fileName"
                Write-Host "  [SKIP] $fileName (already exists)" -ForegroundColor Yellow
                continue
            }
            Remove-Item $targetPath -Force
        }
        
        try {
            cmd /c mklink "$targetPath" "$sourcePath" | Out-Null
            $results.exerciseSymlinks += $fileName
            Write-Host "  [OK] $fileName" -ForegroundColor Green
        } catch {
            $results.errors += "Failed to create symlink for $fileName : $_"
            Write-Host "  [ERROR] $fileName : $_" -ForegroundColor Red
        }
    }
    
    # Get solution files (sol_*.py)
    $solutionFiles = Get-ChildItem -Path $chapterPath -Filter "sol_*.py" -File
    foreach ($file in $solutionFiles) {
        $fileName = $file.Name -replace '\.py$'
        $targetPath = Join-Path $exerciseIndexPath ($fileName + ".py")
        $sourcePath = "..\$chapterName\$($file.Name)"
        
        if (Test-Path $targetPath) {
            if (-not $Force) {
                $results.errors += "Symlink already exists: $fileName"
                continue
            }
            Remove-Item $targetPath -Force
        }
        
        try {
            cmd /c mklink "$targetPath" "$sourcePath" | Out-Null
            $results.solutionSymlinks += $fileName
            Write-Host "  [OK] $fileName" -ForegroundColor Green
        } catch {
            $results.errors += "Failed to create symlink for $fileName : $_"
            Write-Host "  [ERROR] $fileName : $_" -ForegroundColor Red
        }
    }
    
    # Get interlude files (i_*.py)
    $interludes = Get-ChildItem -Path $chapterPath -Filter "i_*.py" -File
    foreach ($file in $interludes) {
        $fileName = $file.Name -replace '\.py$'
        $targetPath = Join-Path $exerciseIndexPath ($fileName + ".py")
        $sourcePath = "..\$chapterName\$($file.Name)"
        
        if (Test-Path $targetPath) {
            if (-not $Force) {
                continue
            }
            Remove-Item $targetPath -Force
        }
        
        try {
            cmd /c mklink "$targetPath" "$sourcePath" | Out-Null
            $results.interludes += $fileName
            Write-Host "  [OK] $fileName" -ForegroundColor Green
        } catch {
            $results.errors += "Failed to create symlink for $fileName : $_"
            Write-Host "  [ERROR] $fileName : $_" -ForegroundColor Red
        }
    }
}

# Get all code files
Write-Host "`nScanning code directories..." -ForegroundColor Cyan
$codePath = "$BasePath\course\code"
$codeChapterDirs = Get-ChildItem -Path $codePath -Directory | Where-Object { $_.Name -match '^ch\d{2}$|^capstones$' }

foreach ($chapterDir in $codeChapterDirs) {
    $chapterPath = $chapterDir.FullName
    $chapterName = $chapterDir.Name
    
    # Get code module files (ch*.py, but not __init__.py)
    $codeFiles = Get-ChildItem -Path $chapterPath -Filter "*.py" -File | Where-Object { $_.Name -match '^ch\d{2}' }
    foreach ($file in $codeFiles) {
        $fileName = $file.Name -replace '\.py$'
        $targetPath = Join-Path $codeIndexPath ($fileName + ".py")
        $sourcePath = "..\$chapterName\$($file.Name)"
        
        if (Test-Path $targetPath) {
            if (-not $Force) {
                continue
            }
            Remove-Item $targetPath -Force
        }
        
        try {
            cmd /c mklink "$targetPath" "$sourcePath" | Out-Null
            $results.codeSymlinks += $fileName
            Write-Host "  [OK] $fileName" -ForegroundColor Green
        } catch {
            $results.errors += "Failed to create symlink for $fileName : $_"
            Write-Host "  [ERROR] $fileName : $_" -ForegroundColor Red
        }
    }
    
    # Get test files (test_*.py)
    $testFiles = Get-ChildItem -Path $chapterPath -Filter "test_*.py" -File
    foreach ($file in $testFiles) {
        $fileName = $file.Name -replace '\.py$'
        $targetPath = Join-Path $codeIndexPath ($fileName + ".py")
        $sourcePath = "..\$chapterName\$($file.Name)"
        
        if (Test-Path $targetPath) {
            if (-not $Force) {
                continue
            }
            Remove-Item $targetPath -Force
        }
        
        try {
            cmd /c mklink "$targetPath" "$sourcePath" | Out-Null
            $results.tests += $fileName
            Write-Host "  [OK] $fileName" -ForegroundColor Green
        } catch {
            $results.errors += "Failed to create symlink for $fileName : $_"
            Write-Host "  [ERROR] $fileName : $_" -ForegroundColor Red
        }
    }
}

# Print summary
Write-Host "`n" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SYMLINK CREATION SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Exercise Files:    $($results.exerciseSymlinks.Count)" -ForegroundColor Green
Write-Host "Code Modules:      $($results.codeSymlinks.Count)" -ForegroundColor Green
Write-Host "Solution Files:    $($results.solutionSymlinks.Count)" -ForegroundColor Green
Write-Host "Interlude Files:   $($results.interludes.Count)" -ForegroundColor Green
Write-Host "Test Files:        $($results.tests.Count)" -ForegroundColor Green
Write-Host "Errors:            $($results.errors.Count)" -ForegroundColor $(if ($results.errors.Count -eq 0) { 'Green' } else { 'Red' })
Write-Host "============================================" -ForegroundColor Cyan

if ($results.errors.Count -gt 0) {
    Write-Host "`nERRORS:" -ForegroundColor Red
    $results.errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

Write-Host "`nIndex directories created at:" -ForegroundColor Cyan
Write-Host "  Exercises: $exerciseIndexPath" -ForegroundColor Yellow
Write-Host "  Code:      $codeIndexPath" -ForegroundColor Yellow
