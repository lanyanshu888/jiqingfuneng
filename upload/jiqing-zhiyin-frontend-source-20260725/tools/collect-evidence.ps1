$ErrorActionPreference = "Stop"

$hdc = "D:\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe"
$app = "D:\JiqingZhiyin\harmony-app\build\outputs\default\harmony-app-default-unsigned.app"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outDir = "D:\JiqingZhiyin\harmony-app\docs\evidence\$stamp"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$target = (& $hdc list targets | Select-Object -First 1).Trim()
if ($target -eq "" -or $target -eq "[Empty]") {
  throw "No emulator or device found. Start a phone emulator first."
}

function Invoke-Hdc {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
  & $hdc -t $target @Args
}

function Capture {
  param(
    [string]$Name,
    [int]$X = 0,
    [int]$Y = 0
  )
  if ($X -gt 0 -and $Y -gt 0) {
    Invoke-Hdc shell uitest uiInput click $X $Y | Out-Null
    Start-Sleep -Milliseconds 900
  }
  $remote = "/data/local/tmp/$Name.png"
  Invoke-Hdc shell uitest screenCap -p $remote | Out-Null
  Invoke-Hdc file recv $remote (Join-Path $outDir "$Name.png") | Out-Null
}

Invoke-Hdc uninstall com.jiqing.zhiyin | Out-Null
Invoke-Hdc install $app | Out-Null
Invoke-Hdc shell aa start -a EntryAbility -b com.jiqing.zhiyin | Out-Null
Start-Sleep -Seconds 2

Capture "01-home"
Capture "02-plan" 396 2650
Capture "03-resource" 660 2650
Capture "04-assistant" 915 2650
Capture "05-mine" 1180 2650

Invoke-Hdc shell aa dump -a com.jiqing.zhiyin | Out-File -Encoding utf8 (Join-Path $outDir "ability-dump.txt")
Invoke-Hdc shell bm dump -n com.jiqing.zhiyin | Out-File -Encoding utf8 (Join-Path $outDir "bundle-dump.txt")

Write-Output "Evidence collected: $outDir"

