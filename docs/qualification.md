# Qualification checklists (IQ / OQ / PQ style, learning material)

Not a GxP validation. Shows the structure used for a workstation build.

## IQ: Installation qualification
- [ ] Hardware model and serial match the inventory record
- [ ] OS version matches the approved baseline
- [ ] Required software installed at approved versions (`Get-UpdateStatus.ps1`)
- [ ] Ansible run log archived, no failed tasks
- [ ] Hostname, owner, location recorded

## OQ: Operational qualification
- [ ] Users and groups exist as defined in the role matrix (Testinfra / Pester)
- [ ] SSH root login and password login disabled
- [ ] Firewall active, default deny incoming
- [ ] Monitoring agent running and reachable on port 9100
- [ ] Automatic security updates enabled

## PQ: Performance qualification
- [ ] Pilot users complete their standard tasks (LIMS client, print, file share) for 5 working days
- [ ] No critical incidents in the pilot wave
- [ ] Wave acceptance criteria met (success rate >= 90 %, <= 2 rollbacks)

Each item gets: tester, date, result (pass / fail), evidence reference.
