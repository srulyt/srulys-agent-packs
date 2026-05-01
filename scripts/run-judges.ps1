# Invoke @eval-judge for every request in a judge manifest, in parallel.
# Usage: pwsh -File scripts\run-judges.ps1 -Manifest <path>
param([Parameter(Mandatory)][string]$Manifest)

$ErrorActionPreference = 'Stop'
$mf = Get-Content $Manifest -Raw | ConvertFrom-Json
$jobs = @()
foreach ($req in $mf.requests) {
    $rid  = $req.id
    $out  = $req.response_file
    $prompt = $req.prompt
    if (Test-Path $out) { Write-Host "[skip] $rid (exists)"; continue }
    $jobs += Start-Job -Name "judge-$rid" -ArgumentList $rid, $prompt, $out -ScriptBlock {
        param($rid, $prompt, $out)
        $resp = copilot -p $prompt --agent eval-judge --allow-all-tools --allow-all-paths --no-ask-user 2>&1 | Out-String
        $clean = $resp -replace "`e\[[0-9;]*[a-zA-Z]", ''
        $clean = $clean -replace '```(?:json)?', ''
        $m = [regex]::Match($clean, '(?s)\{.*\}')
        if (-not $m.Success) {
            $errFile = "$out.err"
            New-Item -ItemType Directory -Force -Path (Split-Path $errFile) | Out-Null
            Set-Content -Path $errFile -Value $clean -Encoding UTF8
            Write-Output "FAIL $rid (no JSON)"
            return
        }
        New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
        Set-Content -Path $out -Value $m.Value -Encoding UTF8
        Write-Output "OK   $rid"
    }
}
Write-Host "Launched $($jobs.Count) judges. Waiting..."
$jobs | Wait-Job | ForEach-Object { Receive-Job $_ } | Write-Host
$jobs | Remove-Job
