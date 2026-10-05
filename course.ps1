# Building Agentic AI Systems: run any course command inside Docker (Windows PowerShell).
# Usage:  .\course.cmd help      (or:  powershell -ExecutionPolicy Bypass -File course.ps1 help)
$ErrorActionPreference = "Continue"
Set-Location -Path $PSScriptRoot
$env:COURSE_HOST_DIR = $PSScriptRoot
New-Item -ItemType Directory -Force -Path "workspace/.sandbox" | Out-Null

$all = @($args)
$cmd = if ($all.Count -gt 0) { "$($all[0])" } else { "help" }

function New-Secret {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return [Convert]::ToBase64String($bytes).Replace("+", "A").Replace("/", "B").TrimEnd("=")
}
function Save-Env($lines) {       # plain UTF-8 without a BOM: Docker Compose can't read a BOM
    [IO.File]::WriteAllLines((Join-Path $PSScriptRoot ".env"), [string[]]$lines, (New-Object Text.UTF8Encoding $false))
}

if ($cmd -eq "setup") {
    Write-Host "== Building Agentic AI Systems: setup =="
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "1. Docker: NOT INSTALLED. Install Docker Desktop: https://docs.docker.com/desktop/setup/install/windows-install/"
        Write-Host "   It needs WSL 2 and hardware virtualization, and admin rights to install."
    } else {
        docker info *> $null
        if ($LASTEXITCODE -ne 0) { Write-Host "1. Docker: installed but NOT RUNNING. Start Docker Desktop." }
        else { Write-Host "1. Docker: OK" }
    }
    if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host "2. Created .env from .env.example" }
    else { Write-Host "2. .env: found" }
    $lines = @(Get-Content ".env")
    $choice = "1"
    $hasKey = $lines | Where-Object { $_ -match '^ANTHROPIC_API_KEY=sk-' -and $_ -notmatch 'your-key-here' }
    if ($lines | Where-Object { $_ -match '^PROVIDER=local' }) {
        $choice = "2"; Write-Host "3. Model: the free local model (PROVIDER=local in .env)"
    } elseif (-not $hasKey) {
        Write-Host "3. Which model do you want to use? (you can switch later in .env; see Appendix H)"
        Write-Host "   1) Claude through the Claude API: best results, pay per use (about `$25-50 for the book)"
        Write-Host "   2) qwen3.5:9b, a free open model on your own computer: needs 16 GB of RAM or more"
        $choice = Read-Host "   Choose 1 or 2 [1]"
    }
    if ($choice -eq "2") {
        if (-not ($lines | Where-Object { $_ -match '^PROVIDER=local' })) {
            $lines = @("PROVIDER=local") + @($lines | Where-Object { $_ -notmatch '^PROVIDER=' })
            Write-Host "   Saved PROVIDER=local. Start the model with:  .\course.cmd local up"
        }
    } else {
        $hasKey = $lines | Where-Object { $_ -match '^ANTHROPIC_API_KEY=sk-' -and $_ -notmatch 'your-key-here' }
        if ($hasKey) { Write-Host "3. API key: already set" }
        else {
            Write-Host "3. API key: paste your Anthropic API key (it starts with sk-ant-; typing is hidden)."
            Write-Host "   Don't have one? See 'Getting an API key' in Chapter 0 of the book."
            if ("$env:ANTHROPIC_API_KEY".StartsWith("sk-")) {
                $key = $env:ANTHROPIC_API_KEY; Write-Host "   Using ANTHROPIC_API_KEY from your environment."
            } else {
                $sec = Read-Host "   Key" -AsSecureString
                $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
            }
            if ($key.StartsWith("sk-")) {
                $lines = @("ANTHROPIC_API_KEY=$key") + @($lines | Where-Object { $_ -notmatch '^ANTHROPIC_API_KEY=' })
                Write-Host "   Saved."
            } else { Write-Host "   That doesn't look like an API key (it should start with sk-). Run setup again." }
        }
    }
    foreach ($name in "AGENT_API_KEYS", "MCP_TOKEN", "MCP_READONLY_TOKEN") {
        if (-not ($lines | Where-Object { $_ -match "^$name=.+" })) { $lines += "$name=$(New-Secret)" }
    }
    Save-Env $lines
    Write-Host "4. Chapter 19 keys: set (random, in .env)"
    Write-Host ""
    Write-Host "Next:  .\course.cmd build   then   .\course.cmd selftest   then   .\course.cmd check --api"
    if ($lines | Where-Object { $_ -match '^PROVIDER=local' }) {
        Write-Host "       (local model: run  .\course.cmd local up  before  check --api)"
    }
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Run .\course.cmd setup for help." -ForegroundColor Red
    exit 1
}
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running. Start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
if ($cmd -ne "build") {
    docker image inspect building-agentic-ai:latest *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "First run: building the course image (this takes a few minutes, once)..."
        docker compose build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}

$rest = if ($all.Count -gt 1) { @($all[1..($all.Count - 1)]) } else { @() }
# which code produced a result: run-chapter records it in every summary.json
if (Get-Command git -ErrorAction SilentlyContinue) {
    $head = git rev-parse --short=12 HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and $head) {
        git diff --quiet HEAD -- course solutions 2>$null
        $env:COURSE_COMMIT = if ($LASTEXITCODE -eq 0) { $head } else { "$head-modified" }
    }
}

switch ($cmd) {
    "build"   { docker compose build @rest }
    "sandbox" {
        $action = if ($rest.Count -gt 0) { $rest[0] } else { "up" }
        switch ($action) {
            "up"     { docker compose --profile sandbox up -d sandbox }
            "down"   { docker compose --profile sandbox stop sandbox }
            "logs"   { docker compose --profile sandbox logs -f sandbox }
            "status" { docker compose --profile sandbox ps sandbox }
            default  { Write-Host "Usage: .\course.cmd sandbox up|down|logs|status" }
        }
    }
    "local" {       # the free local model (Appendix H): up [--gpu|--native] | down | status | logs
        $action = if ($rest.Count -gt 0) { $rest[0] } else { "status" }
        $files = @("-f", "compose.yaml")
        if ($rest -contains "--gpu") { $files += @("-f", "compose.gpu.yaml") }
        switch ($action) {
            "up" {
                if ($rest -contains "--native") { docker compose --profile local up -d local-adapter }
                else { docker compose @files --profile local up -d local-model local-adapter }
                if ($LASTEXITCODE -eq 0) { docker compose run --rm course local-pull }
                if (-not (Select-String -Path ".env" -Pattern '^PROVIDER=local' -Quiet)) {
                    Write-Host "Now set PROVIDER=local in .env to use it, then run: .\course.cmd check --api"
                }
            }
            "down"   { docker compose --profile local stop local-model local-adapter }
            "status" { docker compose --profile local ps local-model local-adapter; docker compose run --rm course local-status }
            "logs"   { docker compose --profile local logs -f local-model local-adapter }
            default  { Write-Host "Usage: .\course.cmd local up [--gpu|--native] | down | status | logs" }
        }
    }
    "mcp"       { docker compose run --rm -T course @rest }
    "inspector" { docker compose run --rm --service-ports course @all }
    "serve"     { docker compose run --rm --service-ports course @all }
    "serve-api" { docker compose run --rm -p 127.0.0.1:8080:8080 --name agentic-ai-api course @all }
    "serve-mcp" { docker compose run --rm -p 127.0.0.1:8000:8000 --name agentic-ai-mcp course @all }
    "serve-a2a" { docker compose run --rm -p 127.0.0.1:9999:9999 --name agentic-ai-a2a -e A2A_PUBLIC_URL=http://agentic-ai-a2a:9999 course @all }
    { $_ -in "ex", "exercise" } {
        if ($rest.Count -gt 0 -and "$($rest[0])".StartsWith("12.")) {
            docker compose run --rm --service-ports course @all
        } else {
            docker compose run --rm course @all
        }
    }
    default { docker compose run --rm course @all }
}
exit $LASTEXITCODE
