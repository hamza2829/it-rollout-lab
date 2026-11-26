# Shared helpers. Scripts read SIMULATED data from JSON so they run on pwsh in Linux CI.
function Read-LabJson {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path $Path)) { throw "File not found: $Path" }
    Get-Content -Raw -Path $Path | ConvertFrom-Json
}

function Compare-LabVersion {
    param([string]$Installed, [string]$Required)
    return ([version]$Installed).CompareTo([version]$Required)
}
Export-ModuleMember -Function Read-LabJson, Compare-LabVersion
