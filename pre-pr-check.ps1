#!/usr/bin/env pwsh
Param()
$script = Join-Path -Path $PSScriptRoot -ChildPath '.github\scripts\pre_pr_interactive.py'
if (-Not (Test-Path $script)) {
    Write-Error "pre_pr_interactive.py not found at $script"
    exit 1
}
python $script