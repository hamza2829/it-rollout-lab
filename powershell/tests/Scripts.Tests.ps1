BeforeAll {
    $root = Split-Path $PSScriptRoot -Parent
    $fx = Join-Path $root 'fixtures'
    $devices = Join-Path $fx 'devices.json'
}

Describe 'Common module' {
    BeforeAll { Import-Module (Join-Path $root 'Common.psm1') -Force }
    It 'compares versions numerically' { Compare-LabVersion '2.10.0' '2.9.0' | Should -Be 1 }
    It 'detects older versions' { Compare-LabVersion '2.1.4' '2.3.0' | Should -Be -1 }
    It 'throws on missing file' { { Read-LabJson '/nope.json' } | Should -Throw }
}

Describe 'Get-UpdateStatus' {
    BeforeAll { $r = & (Join-Path $root 'Get-UpdateStatus.ps1') -InventoryPath $devices -BaselinePath (Join-Path $fx 'baseline.json') }
    It 'finds two pending updates' { @($r).Count | Should -Be 2 }
    It 'flags the old agent on WS-001' { ($r | Where-Object Hostname -eq 'WS-001').Software | Should -Be 'Endpoint Agent' }
    It 'flags old 7-Zip on WS-002' { ($r | Where-Object Hostname -eq 'WS-002').Required | Should -Be '24.8.0' }
}

Describe 'New-LocalLabAccounts' {
    BeforeAll { $a = & (Join-Path $root 'New-LocalLabAccounts.ps1') -RolesPath (Join-Path $fx 'roles.json') }
    It 'plans groups, users and memberships' { @($a).Count | Should -Be 6 }
    It 'creates groups first' { $a[0].Action | Should -Be 'CreateGroup' }
    It 'rejects unknown group' { { & (Join-Path $root 'New-LocalLabAccounts.ps1') -RolesPath (Join-Path $fx 'roles_bad.json') } | Should -Throw }
    It 'refuses Apply on non-Windows' -Skip:$IsWindows { { & (Join-Path $root 'New-LocalLabAccounts.ps1') -RolesPath (Join-Path $fx 'roles.json') -Apply } | Should -Throw }
}

Describe 'Export-SoftwareInventory' {
    It 'writes one row per host and package' {
        $out = Join-Path $TestDrive 'sw.csv'
        $n = & (Join-Path $root 'Export-SoftwareInventory.ps1') -InventoryPath $devices -OutFile $out
        $n | Should -Be 5
        (Import-Csv $out).Count | Should -Be 5
    }
}

Describe 'Test-PreRolloutHealth' {
    BeforeAll { $h = & (Join-Path $root 'Test-PreRolloutHealth.ps1') -InventoryPath $devices }
    It 'marks the healthy device ready' { ($h | Where-Object Hostname -eq 'WS-001').Ready | Should -BeTrue }
    It 'reports warranty, disk and backup issues' {
        ($h | Where-Object Hostname -eq 'WS-002').Issues | Should -Be 'warranty_expired,low_disk,backup_too_old'
    }
    It 'blocks devices that are not active' { ($h | Where-Object Hostname -eq 'WS-003').Issues | Should -Match 'status:in_repair' }
}
