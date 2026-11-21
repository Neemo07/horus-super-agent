param(
  [ValidateSet("project", "global")]
  [string]$Mode = "project",
  [string]$TargetDir = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Mode -eq "global") {
  $Base = Join-Path $HOME ".config/opencode"
  New-Item -ItemType Directory -Force -Path (Join-Path $Base "agents"), (Join-Path $Base "skills") | Out-Null
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/agents/*") (Join-Path $Base "agents")
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/skills/*") (Join-Path $Base "skills")
  if (-not (Test-Path (Join-Path $Base "AGENTS.md"))) { Copy-Item (Join-Path $ScriptDir "AGENTS.md") (Join-Path $Base "AGENTS.md") }
  if (-not (Test-Path (Join-Path $Base "opencode.jsonc"))) { Copy-Item (Join-Path $ScriptDir "opencode.jsonc") (Join-Path $Base "opencode.jsonc") }
  Write-Host "Installed globally to $Base"
} else {
  New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir ".opencode/agents"), (Join-Path $TargetDir ".opencode/skills") | Out-Null
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/agents/*") (Join-Path $TargetDir ".opencode/agents")
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/skills/*") (Join-Path $TargetDir ".opencode/skills")
  if (-not (Test-Path (Join-Path $TargetDir "AGENTS.md"))) { Copy-Item (Join-Path $ScriptDir "AGENTS.md") (Join-Path $TargetDir "AGENTS.md") }
  if (-not (Test-Path (Join-Path $TargetDir "opencode.jsonc"))) { Copy-Item (Join-Path $ScriptDir "opencode.jsonc") (Join-Path $TargetDir "opencode.jsonc") }
  Write-Host "Installed into project: $TargetDir"
}

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Note: Graphify CLI not found. Install it for AST knowledge graphs:"
  Write-Host "  uv tool install --upgrade graphifyy   # or: pip install graphifyy"
}
if (-not (Get-Command rea -ErrorAction SilentlyContinue)) {
  Write-Host "Note: REA CLI not found. Optional for binary reverse engineering:"
  Write-Host "  npx -y rea-agents@latest setup"
}
