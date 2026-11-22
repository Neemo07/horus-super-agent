param(
  [ValidateSet("project", "global")]
  [string]$Mode = "project",
  [string]$TargetDir = (Get-Location).Path,
  [switch]$Force,
  [switch]$V1,
  [switch]$SyncUpstream
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Copy-ConfigFile {
  param([string]$Src, [string]$Dst, [bool]$Overwrite)
  if (Test-Path $Dst) {
    if ($Overwrite) {
      Copy-Item -Force $Dst "$Dst.bak"
      Copy-Item -Force $Src $Dst
      Write-Host "Updated $Dst (backup saved to $Dst.bak)"
    } else {
      Write-Host "Kept existing $Dst (pass -Force to upgrade to v0.2.1)"
    }
  } else {
    Copy-Item $Src $Dst
  }
}

if ($Mode -eq "global") {
  $Base = Join-Path $HOME ".config/opencode"
  $AgentsDst = Join-Path $Base "agents"
  $SkillsDst = Join-Path $Base "skills"
  $CommandsDst = Join-Path $Base "commands"
  $ConfigBase = $Base
} else {
  $AgentsDst = Join-Path $TargetDir ".opencode/agents"
  $SkillsDst = Join-Path $TargetDir ".opencode/skills"
  $CommandsDst = Join-Path $TargetDir ".opencode/commands"
  $ConfigBase = $TargetDir
}

New-Item -ItemType Directory -Force -Path $AgentsDst, $SkillsDst, $CommandsDst | Out-Null
Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/agents/*") $AgentsDst
Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/skills/*") $SkillsDst
if (Test-Path (Join-Path $ScriptDir ".opencode/commands")) {
  Copy-Item -Recurse -Force (Join-Path $ScriptDir ".opencode/commands/*") $CommandsDst
}

Copy-ConfigFile (Join-Path $ScriptDir "AGENTS.md") (Join-Path $ConfigBase "AGENTS.md") $Force.IsPresent
if ($V1) {
  Copy-ConfigFile (Join-Path $ScriptDir "opencode.v1.json") (Join-Path $ConfigBase "opencode.json") $Force.IsPresent
} else {
  Copy-ConfigFile (Join-Path $ScriptDir "opencode.jsonc") (Join-Path $ConfigBase "opencode.jsonc") $Force.IsPresent
}

if ($SyncUpstream) {
  & (Join-Path $ScriptDir "scripts/sync-skills.ps1") -SkillsDir $SkillsDst -CommandsDir $CommandsDst
}

Write-Host "Installed Horus Super Agent v0.2.1 ($Mode) -> $ConfigBase"

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Note: Graphify CLI not found. Optional AST knowledge graph:"
  Write-Host "  uv tool install --upgrade graphifyy   # or: pip install graphifyy"
}
if (-not (Get-Command rea -ErrorAction SilentlyContinue)) {
  Write-Host "Note: REA CLI not found. Optional for binary reverse engineering:"
  Write-Host "  npx -y rea-agents@latest setup"
}
