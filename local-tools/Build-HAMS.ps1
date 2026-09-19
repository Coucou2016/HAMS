param(
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

function Convert-ToMsysPath {
    param([string]$Path)
    $Resolved = (Resolve-Path -LiteralPath $Path).Path.Replace("\", "/")
    if ($Resolved -match "^([A-Za-z]):/(.*)$") {
        return "/$($Matches[1].ToLower())/$($Matches[2])"
    }
    return $Resolved
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Bash = Join-Path $ProjectRoot ".tools\msys64\usr\bin\bash.exe"
$MingwBin = Join-Path $ProjectRoot ".tools\msys64\mingw64\bin"
$Ld = Join-Path $MingwBin "ld.exe"
$LdBfd = Join-Path $MingwBin "ld.bfd.exe"

if (-not (Test-Path -LiteralPath $Bash -PathType Leaf)) {
    throw "Local MSYS2 bash was not found: $Bash"
}

if ((-not (Test-Path -LiteralPath $Ld -PathType Leaf)) -and (Test-Path -LiteralPath $LdBfd -PathType Leaf)) {
    Copy-Item -LiteralPath $LdBfd -Destination $Ld -Force
}

$SourcePath = Convert-ToMsysPath (Join-Path $ProjectRoot "SourceCode")
$BuildCommand = "export PATH=/mingw64/bin:/usr/bin:`$PATH; cd '$SourcePath'; "
if (-not $NoClean) {
    $BuildCommand += "make clean; "
}
$BuildCommand += "make OS=Windows_NT FC=gfortran"

& $Bash -lc $BuildCommand
exit $LASTEXITCODE
