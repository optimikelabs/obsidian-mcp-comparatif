param([string]$Root)
$ErrorActionPreference = 'Stop'
$log = Join-Path $Root 'preuves\memoire.jsonl'
$stop = Join-Path $Root 'ARRET-MEMOIRE.json'
$end = Join-Path $Root 'FIN-SURVEILLANCE'
while (-not (Test-Path -LiteralPath $end)) {
  $m = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
  $v = [ordered]@{utc=[DateTime]::UtcNow.ToString('o');commitFreeBytes=[long]($m.CommitLimit-$m.CommittedBytes);availableBytes=[long]$m.AvailableBytes}
  $v | ConvertTo-Json -Compress | Add-Content -LiteralPath $log -Encoding utf8
  if ($v.commitFreeBytes -lt 1.5GB) { $v | ConvertTo-Json | Set-Content -LiteralPath $stop -Encoding utf8; break }
  Start-Sleep -Seconds 1
}
