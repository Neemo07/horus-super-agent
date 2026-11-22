param(
  [string]$SkillsDir = (Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) ".opencode/skills"),
  [string]$CommandsDir = (Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) ".opencode/commands")
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required to sync upstream skills."
}

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("horus-skill-sync-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

function Sync-Subdir {
  param([string]$RepoUrl, [string]$SubPath, [string]$DestDir, [string]$Label)
  Write-Host "Syncing $Label from $RepoUrl ..."
  $CloneDir = Join-Path $Tmp ($Label -replace '[^a-zA-Z0-9_-]', '_')
  try {
    git clone --depth 1 --filter=blob:none --sparse $RepoUrl $CloneDir 2>$null
    if ($SubPath -ne ".") {
      git -C $CloneDir sparse-checkout set $SubPath 2>$null
      $Src = Join-Path $CloneDir $SubPath
    } else {
      $Src = $CloneDir
    }
    if (Test-Path $Src) {
      New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
      Copy-Item -Recurse -Force (Join-Path $Src "*") $DestDir
      Write-Host "  OK -> $DestDir"
    } else {
      Write-Warning "  Path '$SubPath' not found in $RepoUrl; keeping bundled version."
    }
  } catch {
    Write-Warning "  Could not sync $Label ($($_.Exception.Message)); keeping bundled version."
  }
}

try {
  Sync-Subdir "https://github.com/abduallahJamal/vibe-engineering-playbook.git" ".opencode/skills" $SkillsDir "vibe-skills"
  Sync-Subdir "https://github.com/abduallahJamal/vibe-engineering-playbook.git" ".opencode/commands" $CommandsDir "vibe-commands"
  Sync-Subdir "https://github.com/anthropics/skills.git" "skills/frontend-design" (Join-Path $SkillsDir "frontend-design") "frontend-design"
  Sync-Subdir "https://github.com/anthropics/skills.git" "skills/webapp-testing" (Join-Path $SkillsDir "webapp-testing") "webapp-testing"
  Sync-Subdir "https://github.com/obra/superpowers.git" "skills" (Join-Path $SkillsDir "superpowers/upstream-skills") "superpowers-core"
  Sync-Subdir "https://github.com/vercel-labs/agent-skills.git" "skills/react-best-practices" (Join-Path $SkillsDir "vercel-react-best-practices") "vercel-react-best-practices"
  Sync-Subdir "https://github.com/supabase/agent-skills.git" "skills/supabase-postgres-best-practices" (Join-Path $SkillsDir "supabase-postgres-best-practices") "supabase-postgres-best-practices"
} finally {
  Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}

Write-Host "Upstream skill sync complete."
