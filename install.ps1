param(
  [ValidateSet("project", "global")]
  [string]$Mode = "project",
  [string]$TargetDir = (Get-Location).Path,
  [switch]$ForceConfig
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Copy-JsoncAsStrictJson {
  param(
    [string]$SourcePath,
    [string]$DestPath
  )
  $lines = Get-Content -Path $SourcePath -Encoding UTF8 | Where-Object { $_ -notmatch '^\s*//' }
  $cleaned = ($lines -join "`n") -replace ',(\s*[}\]])', '$1'
  # Validate JSON before writing
  $null = $cleaned | ConvertFrom-Json
  [System.IO.File]::WriteAllText($DestPath, $cleaned + "`n", [System.Text.UTF8Encoding]::new($false))
}

if ($Mode -eq "global") {
  $Base = Join-Path $HOME ".config/opencode"
  $Cfg  = $Base
} else {
  $Base = Join-Path $TargetDir ".opencode"
  $Cfg  = $TargetDir
}

foreach ($d in "agents", "skills", "commands") {
  New-Item -ItemType Directory -Force -Path (Join-Path $Base $d) | Out-Null
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/$d/*") (Join-Path $Base $d)
}

foreach ($f in "AGENTS.md", "opencode.jsonc") {
  $destFile = Join-Path $Cfg $f
  $writeStrictJson = $false

  # Global installs usually already have an opencode.json holding providers/MCP.
  # Dropping a competing opencode.jsonc beside it risks shadowing that config,
  # so never introduce a second config file in global mode; when creating a fresh
  # global opencode.json, strip JSONC comments so strict JSON parsers succeed.
  if ($f -eq "opencode.jsonc" -and $Mode -eq "global") {
    $existingJson = Join-Path $Cfg "opencode.json"
    if (Test-Path $existingJson) {
      Write-Host "Skipped $destFile (opencode.json already exists; add permissions manually)"
      continue
    }
    $destFile = $existingJson
    $writeStrictJson = $true
  }

  $srcFile = Join-Path $ScriptDir $f
  if (Test-Path $destFile) {
    if ($ForceConfig) {
      Copy-Item -Force $destFile "$destFile.bak"
      if ($writeStrictJson) {
        Copy-JsoncAsStrictJson -SourcePath $srcFile -DestPath $destFile
      } else {
        Copy-Item -Force $srcFile $destFile
      }
      Write-Host "Updated $destFile (backup saved to $destFile.bak)"
    } else {
      Write-Host "Kept existing $destFile (pass -ForceConfig to upgrade with .bak backup)"
    }
  } else {
    if ($writeStrictJson) {
      Copy-JsoncAsStrictJson -SourcePath $srcFile -DestPath $destFile
    } else {
      Copy-Item $srcFile $destFile
    }
  }
}

New-Item -ItemType Directory -Force -Path (Join-Path $Cfg "scripts") | Out-Null
foreach ($s in "sync_upstream.py", "validate_horus.py", "migrate-opencode-db.py") {
  Copy-Item -Force (Join-Path $ScriptDir "scripts/$s") (Join-Path $Cfg "scripts/$s")
}
Write-Host "Installed Horus v0.3.7 ($Mode) to $Base"

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Note: Graphify CLI not found (AST knowledge graphs):  uv tool install --upgrade "graphifyy[mcp]""
}
if (-not (Get-Command rea -ErrorAction SilentlyContinue)) {
  Write-Host "Note: REA CLI not found (binary reverse engineering, optional):  npx -y rea-agents@latest setup"
}

if (Get-Command python -ErrorAction SilentlyContinue) {
  python (Join-Path $Cfg "scripts/validate_horus.py")
  # Quietly probe Playwright. `cmd /c` fully isolates the child's streams:
  # under $ErrorActionPreference = "Stop", PowerShell 5.1 otherwise converts
  # a native ImportError traceback on stderr into a terminating error.
  cmd /c "python -c ""import playwright"" >nul 2>&1"
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Note: 'webapp-testing' needs Playwright:  pip install playwright; python -m playwright install chromium"
  }
}
Write-Host "Optional: sync other upstream skills:  python $(Join-Path $Cfg 'scripts/sync_upstream.py') --dest $(Join-Path $Base 'skills')"
