<#
.SYNOPSIS Pre-rollout health check per device: status, warranty, disk space, backup age.
#>
param(
    [Parameter(Mandatory)][string]$InventoryPath,
    [string]$RolloutDate = '2026-02-02',
    [int]$MinFreeGB = 10,
    [int]$MaxBackupAgeDays = 7
)
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force
$date = [datetime]::ParseExact($RolloutDate, 'yyyy-MM-dd', $null)
foreach ($d in (Read-LabJson $InventoryPath)) {
    $issues = @()
    if ($d.status -ne 'active') { $issues += "status:$($d.status)" }
    if ([datetime]::ParseExact($d.warranty_end, 'yyyy-MM-dd', $null) -lt $date) { $issues += 'warranty_expired' }
    if ($null -ne $d.free_disk_gb -and $d.free_disk_gb -lt $MinFreeGB) { $issues += 'low_disk' }
    if ($null -ne $d.last_backup -and ($date - [datetime]$d.last_backup).Days -gt $MaxBackupAgeDays) { $issues += 'backup_too_old' }
    [pscustomobject]@{ Hostname = $d.hostname; Ready = ($issues.Count -eq 0); Issues = ($issues -join ',') }
}
