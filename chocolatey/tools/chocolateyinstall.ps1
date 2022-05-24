$ErrorActionPreference = 'Stop'; # stop on all errors
[String] $cmd = "C:\Python35\Scripts\pip3.exe"
[Array]  $cmdargs = @(
  'install', '--upgrade', '--extra-index-url', 
  'http://artifactory.amer.gettywan.com/artifactory/api/pypi/getty-pypi/simple',
  '--trusted-host', 'artifactory.amer.gettywan.com', 'springboardcli'
)



$install = Start-Process $cmd -ArgumentList $cmdargs -PassThru -NoNewWindow -Wait
if ($install.ExitCode -eq 1) {exit 1} else {exit 0}