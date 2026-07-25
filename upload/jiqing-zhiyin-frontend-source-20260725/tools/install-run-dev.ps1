$ErrorActionPreference = "Stop"

$hdc = "D:\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe"
$app = "D:\JiqingZhiyin\harmony-app\build\outputs\default\harmony-app-default-unsigned.app"
$target = (& $hdc list targets | Select-Object -First 1).Trim()

if ($target -eq "" -or $target -eq "[Empty]") {
  throw "No emulator or device found. Start a phone emulator first."
}

& $hdc -t $target uninstall com.jiqing.zhiyin
& $hdc -t $target install $app
& $hdc -t $target shell aa start -a EntryAbility -b com.jiqing.zhiyin
