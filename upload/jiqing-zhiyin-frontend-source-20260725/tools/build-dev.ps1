$ErrorActionPreference = "Stop"

$project = "D:\JiqingZhiyin\harmony-app"
$node = "D:\DevEco Studio\tools\node\node.exe"
$hvigor = "D:\DevEco Studio\tools\hvigor\bin\hvigorw.js"
$env:DEVECO_SDK_HOME = "D:\DevEco Studio\sdk"
$env:JAVA_HOME = "D:\DevEco Studio\jbr"
$env:Path = "D:\DevEco Studio\jbr\bin;" + $env:Path

Set-Location $project
& $node $hvigor PackageApp --no-daemon

