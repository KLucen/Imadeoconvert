$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$compilerDir = Join-Path $projectRoot 'tools/innosetup-6.7.3'
$installerPath = Join-Path $projectRoot '.cache/innosetup-6.7.3.exe'
$expectedHash = '9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732'
if (-not (Test-Path -LiteralPath $installerPath)) {
    New-Item -ItemType Directory -Path (Split-Path $installerPath) -Force | Out-Null
    Invoke-WebRequest -Uri 'https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe' -OutFile $installerPath -TimeoutSec 120
}
if ((Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLower() -ne $expectedHash) {
    throw 'Inno Setup download checksum mismatch'
}
$signature = Get-AuthenticodeSignature -LiteralPath $installerPath
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Pyrsys B.V.') {
    throw 'Inno Setup publisher signature could not be verified'
}
$compilerPath = Join-Path $compilerDir 'ISCC.exe'
if (-not (Test-Path -LiteralPath $compilerPath)) {
    if (Test-Path -LiteralPath $compilerDir) { throw 'Preserving an incomplete existing compiler directory' }
    $install = Start-Process -FilePath $installerPath -ArgumentList @(
        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/PORTABLE=1',
        '/CURRENTUSER', '/NOICONS', '/TASKS=""', ('/DIR="' + $compilerDir + '"')
    ) -WindowStyle Hidden -PassThru -Wait
    if ($install.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $compilerPath)) {
        throw 'Inno Setup portable compiler extraction failed'
    }
}
Write-Output $compilerPath
