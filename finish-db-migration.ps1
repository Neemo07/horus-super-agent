# Finish the OpenCode DB migration.
# Run this AFTER closing the OpenCode Desktop app (and any terminal running `opencode`).
# It is safe to re-run: it always takes a fresh backup before changing anything.

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script  = Join-Path $RepoDir "scripts\migrate-opencode-db.py"
$Db      = Join-Path $HOME ".local\share\opencode\opencode.db"

if (-not (Test-Path $Script)) { throw "Missing: $Script" }
if (-not (Test-Path $Db))     { throw "Missing: $Db" }

Write-Host "Checking for a running OpenCode..." -ForegroundColor Cyan
$procs = Get-CimInstance Win32_Process -Filter "Name LIKE '%opencode%'" |
    Select-Object ProcessId, Name

if ($procs) {
    Write-Host ""
    Write-Host "OpenCode is still running. Close it completely, then run this again:" -ForegroundColor Yellow
    $procs | Format-Table -AutoSize | Out-String | Write-Host
    Write-Host "Note: if you launched this from inside OpenCode, that session holds the DB." -ForegroundColor Yellow
    exit 1
}

Write-Host "No OpenCode processes found. Starting migration..." -ForegroundColor Green
python $Script --db $Db
$code = $LASTEXITCODE

if ($code -eq 0) {
    Write-Host ""
    Write-Host "Migration finished." -ForegroundColor Green
    Write-Host "Verify with:" -ForegroundColor Cyan
    Write-Host "  opencode session list -n 5"
} else {
    Write-Host ""
    Write-Host "Migration did not complete (exit $code). Your original DB is untouched." -ForegroundColor Red
}
exit $code
