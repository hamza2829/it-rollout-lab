<#
.SYNOPSIS Compare installed software with the approved baseline and list pending updates.
#>
param(
    [Parameter(Mandatory)][string]$InventoryPath,
    [Parameter(Mandatory)][string]$BaselinePath
)
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force
$devices = Read-LabJson $InventoryPath
$baseline = Read-LabJson $BaselinePath
foreach ($d in $devices) {
    foreach ($p in $baseline.PSObject.Properties) {
        $installed = $d.software.($p.Name)
        if ($null -eq $installed) { continue }
        if ((Compare-LabVersion $installed $p.Value) -lt 0) {
            [pscustomobject]@{ Hostname = $d.hostname; Software = $p.Name; Installed = $installed; Required = $p.Value }
        }
    }
}
