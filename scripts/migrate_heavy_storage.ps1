param([Parameter(Mandatory=$true)][string]$PlanPath)
$ErrorActionPreference='Stop'
$plan=Get-Content -LiteralPath $PlanPath -Raw -Encoding utf8 | ConvertFrom-Json
$base=[IO.Path]::GetFullPath($plan.source_root).TrimEnd('\')
$archive=[IO.Path]::GetFullPath($plan.destination_root).TrimEnd('\')
if (-not $base.EndsWith('\test-comparatif') -or ([IO.Path]::GetPathRoot($archive) -ne 'B:\')) { throw 'Racines non autorisées' }
$receipts=Join-Path (Split-Path -Parent $PlanPath) 'manifestes'
New-Item -ItemType Directory -Path $receipts -Force | Out-Null
function Inventory([string]$Root) {
 $files=@(Get-ChildItem -LiteralPath $Root -Recurse -Force -File)
 $items=@(Get-ChildItem -LiteralPath $Root -Recurse -Force)
 if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw "Lien interne refusé : $Root" }
 @($files | Sort-Object FullName | ForEach-Object {
  [pscustomobject]@{path=$_.FullName.Substring($Root.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower();creation_utc=$_.CreationTimeUtc.ToString('o');modified_utc=$_.LastWriteTimeUtc.ToString('o')}
 })
}
function Same($Left,$Right) {
 if ($Left.Count -ne $Right.Count) { throw 'Nombre de fichiers différent' }
 $lookup=@{};foreach($r in $Right){$lookup[$r.path]=$r}
 foreach($l in $Left){$r=$lookup[$l.path];if (-not $r -or $r.bytes -ne $l.bytes -or $r.sha256 -ne $l.sha256){throw "SHA-256 différent : $($l.path)"}}
}
$i=0
foreach($item in $plan.items){
 $i++;$src=[IO.Path]::GetFullPath($item.source);$dst=[IO.Path]::GetFullPath($item.destination)
 if (-not $src.StartsWith($base+'\') -or -not $dst.StartsWith($archive+'\')){throw 'Chemin hors périmètre'}
 $rel=$src.Substring($base.Length+1)
 if ($rel -ne 'installations' -and $rel -notmatch '^resultats\\cellules\\C\d\d-T\db?-r\d[^\\]*\\(vault|profile)$'){throw "Cible non autorisée $rel"}
 if ($dst -ne (Join-Path $archive $rel)){throw 'Arborescence différente'}
 if ((Get-Item -LiteralPath $src -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Source déjà transférée : aucun rejeu'}
 if (Test-Path -LiteralPath $dst){throw 'Destination existante : aucun écrasement'}
 if ($item.cell_id -and -not (Test-Path -LiteralPath (Join-Path $base ('kit\public\resultats\cellules\'+$item.cell_id+'\result.json')))){throw 'Cellule non publiée'}
 $active=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('Obsidian.exe','node.exe','python.exe') -and $_.CommandLine -and ($_.CommandLine.Contains($src) -or ($rel -ne 'installations' -and $_.CommandLine.Contains((Split-Path -Parent $src)+'\'))) })
 if ($active.Count){throw 'Processus lié à la source : transfert interdit'}
 Write-Output ("Copie {0}/{1} : {2}" -f $i,$plan.items.Count,$rel)
 $before=@(Inventory $src)
 $dirs=@(Get-ChildItem -LiteralPath $src -Recurse -Force -Directory | ForEach-Object {[pscustomobject]@{path=$_.FullName.Substring($src.Length+1);creation=$_.CreationTimeUtc;modified=$_.LastWriteTimeUtc}})
 New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null
 Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
 foreach($f in $before){$df=Get-Item -LiteralPath (Join-Path $dst $f.path) -Force;$df.CreationTimeUtc=[datetime]$f.creation_utc;$df.LastWriteTimeUtc=[datetime]$f.modified_utc}
 foreach($d in ($dirs | Sort-Object { $_.path.Length } -Descending)){$dd=Get-Item -LiteralPath (Join-Path $dst $d.path) -Force;$dd.CreationTimeUtc=$d.creation;$dd.LastWriteTimeUtc=$d.modified}
 Same $before @(Inventory $dst)
 Same $before @(Inventory $src)
 $receipt=[ordered]@{source=$src;destination=$dst;relative_path=$rel;copied_verified_sha256=$true;source_removed=$false;junction_verified=$false;files=$before;bytes=($before | Measure-Object bytes -Sum).Sum;verified_utc=[datetime]::UtcNow.ToString('o')}
 $receiptPath=Join-Path $receipts ('{0:D3}.json' -f $i)
 $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
 # Validation finale du chemin absolu, avant tout retrait récursif.
 $resolved=(Resolve-Path -LiteralPath $src).Path
 if ($resolved -ne $src -or -not $resolved.StartsWith($base+'\') -or ((Get-Item -LiteralPath $src -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Source finale non conforme'}
 Remove-Item -LiteralPath $src -Recurse -Force
 $receipt.source_removed=$true
 $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
 New-Item -ItemType Junction -Path $src -Target $dst | Out-Null
 $link=Get-Item -LiteralPath $src -Force
 if ($link.LinkType -ne 'Junction' -or $link.Target -ne $dst){throw 'Jonction incorrecte'}
 Same $before @(Inventory $src)
 $receipt.junction_verified=$true
 $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
 Write-Output ("Vérifié et transféré : {0} octets" -f $receipt.bytes)
}
