param([string]$Path)

$ErrorActionPreference = 'Stop'

# 1) 인코딩 감지 (UTF-16LE BOM, UTF-8 BOM, 그 외)
$bytes = [IO.File]::ReadAllBytes($Path)
if ($bytes.Length -ge 2 -and $bytes[0] -eq 255 -and $bytes[1] -eq 254) {
  $enc = 'Unicode'
}
elseif ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
  $enc = 'utf8'
}
else {
  $enc = 'Default'
}

# 2) 라인별 파싱
Get-Content -Path $Path -Encoding $enc | ForEach-Object {
  $t = $_.Trim()
  if ([string]::IsNullOrWhiteSpace($t) -or $t.StartsWith('#')) { return }
  $i = $t.IndexOf('=')
  if ($i -lt 1) { return }
  $k = $t.Substring(0, $i).Trim()
  $v = $t.Substring($i + 1).Trim().Trim('"')
  Write-Output "$k=$v"
}
