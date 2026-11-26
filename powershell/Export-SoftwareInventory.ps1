<#
.SYNOPSIS Flatten device software lists into a CSV (one row per host and package).
#>
param(
    [Parameter(Mandatory)][string]$InventoryPath,
    [Parameter(Mandatory)][string]$OutFile
)
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force
$rows = foreach ($d in (Read-LabJson $InventoryPath)) {
    foreach ($p in $d.software.PSObject.Properties) {
        [pscustomobject]@{ Hostname = $d.hostname; OS = $d.os; Software = $p.Name; Version = $p.Value }
    }
}
$rows | Sort-Object Hostname, Software | Export-Csv -Path $OutFile -NoTypeInformation
$rows.Count
