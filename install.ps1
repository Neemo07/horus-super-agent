param(
  [ValidateSet("project", "global")]
  [string]$Mode = "project",
  [string]$TargetDir = (Get-Location).Path,
  [switch]$ForceConfig
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

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
  if (Test-Path $destFile) {
    if ($ForceConfig) {
      Copy-Item -Force $destFile "$destFile.bak"
      Copy-Item -Force (Join-Path $ScriptDir $f) $destFile
      Write-Host "Updated $destFile (backup saved to $destFile.bak)"
    } else {
      Write-Host "Kept existing $destFile (pass -ForceConfig to upgrade with .bak backup)"
    }
  } else {
    Copy-Item (Join-Path $ScriptDir $f) $destFile
  }
}

New-Item -ItemType Directory -Force -Path (Join-Path $Cfg "scripts") | Out-Null
Copy-Item -Force (Join-Path $ScriptDir "scripts/sync_upstream.py") (Join-Path $Cfg "scripts/sync_upstream.py")
Copy-Item -Force (Join-Path $ScriptDir "scripts/validate_horus.py") (Join-Path $Cfg "scripts/validate_horus.py")
Write-Host "Installed Horus v0.3 ($Mode) to $Base"

if ($Mode -eq "project" -and (Get-Command python -ErrorAction SilentlyContinue)) {
  python (Join-Path $Cfg "scripts/validate_horus.py")
}

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Note: Graphify CLI not found (AST knowledge graphs):  uv tool install --upgrade graphifyy"
}
if (-not (Get-Command rea -ErrorAction SilentlyContinue)) {
  Write-Host "Note: REA CLI not found (binary reverse engineering, optional):  npx -y rea-agents@latest setup"
}
python -c "import playwright" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Note: 'webapp-testing' needs Playwright:  pip install playwright; python -m playwright install chromium"
}
Write-Host "Optional: sync other upstream skills:  python $(Join-Path $Cfg 'scripts/sync_upstream.py') --dest $(Join-Path $Base 'skills')"
