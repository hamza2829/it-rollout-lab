<#
.SYNOPSIS Build the local user and group setup from a role definition.
.DESCRIPTION On Windows with -Apply it calls New-LocalGroup/New-LocalUser/Add-LocalGroupMember.
             Without -Apply (default, and always in Linux CI) it only returns the planned actions.
#>
param(
    [Parameter(Mandatory)][string]$RolesPath,
    [switch]$Apply
)
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force
$roles = Read-LabJson $RolesPath
$actions = [System.Collections.Generic.List[object]]::new()
foreach ($g in $roles.groups) {
    if ($g -notmatch '^[A-Za-z][A-Za-z0-9_-]{2,30}$') { throw "Invalid group name: $g" }
    $actions.Add([pscustomobject]@{ Action = 'CreateGroup'; Name = $g; Group = $null })
}
foreach ($u in $roles.users) {
    if ($u.group -notin $roles.groups) { throw "User $($u.name) references unknown group $($u.group)" }
    $actions.Add([pscustomobject]@{ Action = 'CreateUser'; Name = $u.name; Group = $null })
    $actions.Add([pscustomobject]@{ Action = 'AddMember'; Name = $u.name; Group = $u.group })
}
if ($Apply) {
    if (-not $IsWindows) { throw 'Apply is only supported on Windows hosts' }
    foreach ($a in $actions) {
        switch ($a.Action) {
            'CreateGroup' { New-LocalGroup -Name $a.Name -ErrorAction SilentlyContinue | Out-Null }
            'CreateUser'  { New-LocalUser -Name $a.Name -NoPassword -ErrorAction SilentlyContinue | Out-Null }
            'AddMember'   { Add-LocalGroupMember -Group $a.Group -Member $a.Name -ErrorAction SilentlyContinue }
        }
    }
}
$actions
