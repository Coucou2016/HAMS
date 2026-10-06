param(
    [string]$Python = "",
    [switch]$FullRecompute,
    [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$localPaperPython = Join-Path $root ".tools\paper-env\Scripts\python.exe"
if ([string]::IsNullOrWhiteSpace($Python)) {
    $Python = if (Test-Path -LiteralPath $localPaperPython) { $localPaperPython } else { "python" }
}

function Invoke-CheckedStep {
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$Arguments
    )
    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

Push-Location $root
try {
    if ($FullRecompute) {
        Invoke-CheckedStep "Recompute hydro-mechanical project evidence" "powershell" @(
            "-ExecutionPolicy", "Bypass", "-File", ".\local-tools\Run-RocketRecoveryPipeline.ps1", "-FastChrono", "-NoServerHint"
        )
    }

    Invoke-CheckedStep "Recompute Yang 2026 evidence and paper figures" "powershell" @(
        "-ExecutionPolicy", "Bypass", "-File", ".\local-tools\Run-Yang2026-PaperPipeline.ps1", "-Python", $Python
    )
    Invoke-CheckedStep "Refresh model realism audit" $Python @(".\analysis\rocket_recovery\model_realism_audit.py", "report")
    Invoke-CheckedStep "Refresh final acceptance audit" $Python @(".\analysis\rocket_recovery\final_acceptance_audit.py", "report")
    Invoke-CheckedStep "Generate research-integrity audit" $Python @(".\analysis\rocket_recovery\paper_integrity_audit.py", "report")
    Invoke-CheckedStep "Build manuscript DOCX" $Python @(".\paper\yang_2026_extension\build_manuscript_docx.py")
    Invoke-CheckedStep "Build research-integrity audit DOCX" $Python @(".\paper\yang_2026_extension\build_integrity_audit_docx.py")

    if (-not $SkipPdf) {
        Invoke-CheckedStep "Export manuscript PDF with Microsoft Word" "powershell" @(
            "-ExecutionPolicy", "Bypass", "-File", ".\local-tools\Export-SeaLanding-Manuscript.ps1"
        )
        Invoke-CheckedStep "Export research-integrity audit PDF with Microsoft Word" "powershell" @(
            "-ExecutionPolicy", "Bypass", "-File", ".\local-tools\Export-SeaLanding-Manuscript.ps1",
            "-InputPath", ".\paper\yang_2026_extension\Research_Integrity_Audit_CN_TheoryFramework.docx",
            "-OutputPath", ".\paper\yang_2026_extension\Research_Integrity_Audit_CN_TheoryFramework.pdf"
        )
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Paper build completed." -ForegroundColor Green
Write-Host "DOCX: $root\paper\yang_2026_extension\Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.docx"
Write-Host "Audit DOCX: $root\paper\yang_2026_extension\Research_Integrity_Audit_CN_TheoryFramework.docx"
if (-not $SkipPdf) {
    Write-Host "PDF:  $root\paper\yang_2026_extension\Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.pdf"
    Write-Host "Audit PDF: $root\paper\yang_2026_extension\Research_Integrity_Audit_CN_TheoryFramework.pdf"
}
