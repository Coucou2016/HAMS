param(
    [string]$CaseDir = "."
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $ProjectRoot "SourceCode\hams.exe"
$MingwBin = Join-Path $ProjectRoot ".tools\msys64\mingw64\bin"

if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) {
    throw "Compiled HAMS executable was not found: $Exe. Run local-tools\Build-HAMS.ps1 first."
}

if (-not (Test-Path -LiteralPath $MingwBin -PathType Container)) {
    throw "Local MinGW runtime was not found: $MingwBin"
}

$ResolvedCase = (Resolve-Path -LiteralPath $CaseDir).Path
$InputDir = Join-Path $ResolvedCase "Input"
$OutputDir = Join-Path $ResolvedCase "Output"

if (-not (Test-Path -LiteralPath $InputDir -PathType Container)) {
    throw "Case directory must contain an Input folder: $InputDir"
}

if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Push-Location -LiteralPath $ResolvedCase
try {
    $env:PATH = "$MingwBin;$env:PATH"
    & $Exe
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
