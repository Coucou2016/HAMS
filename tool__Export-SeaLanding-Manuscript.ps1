param(
    [string]$InputPath = ".\paper\yang_2026_extension\Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.docx",
    [string]$OutputPath = ".\paper\yang_2026_extension\Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.pdf"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$inputFile = [System.IO.Path]::GetFullPath((Join-Path $root $InputPath))
$outputFile = [System.IO.Path]::GetFullPath((Join-Path $root $OutputPath))

if (-not (Test-Path -LiteralPath $inputFile)) {
    throw "Manuscript DOCX not found: $inputFile"
}

$word = $null
$document = $null
$exported = $false
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($inputFile, $false, $true)
    $document.ExportAsFixedFormat($outputFile, 17)
    $exported = Test-Path -LiteralPath $outputFile
    Write-Host "Exported manuscript PDF: $outputFile"
}
finally {
    if ($null -ne $document) {
        try { $document.Close($false) } catch { Write-Verbose "Word document was already closed: $($_.Exception.Message)" }
        try { [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) } catch { }
    }
    if ($null -ne $word) {
        try { $word.Quit() } catch { Write-Verbose "Word process was already unavailable: $($_.Exception.Message)" }
        try { [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) } catch { }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

if (-not $exported -or -not (Test-Path -LiteralPath $outputFile)) {
    throw "Microsoft Word did not produce the requested PDF: $outputFile"
}
