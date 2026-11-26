# Rollout plan: Endpoint Agent 2.3.0 (CHG-2026-014)

Learning project with simulated machines. Not GxP validated.

Eligible workstations: 36, excluded: 10

## Wave 1: Pilot (IT and QA) (6 machines)

| Host | Department | Location | OS | Owner |
|---|---|---|---|---|
| WS-001 | QA | QA Lab | Windows 11 23H2 | user01 |
| WS-002 | IT | IT Office | Windows 11 23H2 | user02 |
| WS-009 | IT | IT Office | Windows 11 23H2 | user09 |
| WS-011 | QA | QA Lab | Windows 11 23H2 | user11 |
| WS-013 | QA | QA Lab | Windows 11 23H2 | user13 |
| WS-014 | IT | IT Office | Windows 11 23H2 | user14 |

**Test phase:** pre-check (warranty, disk, backup), deploy, functional test (agent heartbeat, LIMS client start, print test).

**Acceptance criteria:** success rate of attempted machines at least 90%, at most 2 rollbacks, no open critical incident.

**Rollback steps:**
1. Stop the deployment job for the wave
2. Uninstall the new agent version via software deployment
3. Reinstall the previous approved version from the definitive software library
4. Verify agent heartbeat and functional test on each affected machine
5. Record deviation and rollback in the change record

**Go / no-go checklist:**
- [ ] Change record approved by change board (CHG number recorded)
- [ ] Previous wave acceptance criteria met
- [ ] Rollback package tested on a reference machine
- [ ] Backup of user profiles confirmed
- [ ] Service desk briefed and on standby
- [ ] No production campaign or audit scheduled in the window
- [ ] QA notified (learning project: no GxP release)

## Wave 2: Early adopters (12 machines)

| Host | Department | Location | OS | Owner |
|---|---|---|---|---|
| WS-003 | Logistics | Warehouse | Windows 11 23H2 | user03 |
| WS-004 | Logistics | Warehouse | Ubuntu 22.04 LTS | user04 |
| WS-005 | Logistics | Warehouse | Windows 11 23H2 | user05 |
| WS-006 | Production | Production Hall A | Windows 11 23H2 | user06 |
| WS-007 | Production | Production Hall A | Windows 11 23H2 | user07 |
| WS-008 | Admin | Admin Building | Ubuntu 22.04 LTS | user08 |
| WS-010 | Production | Production Hall A | Windows 11 23H2 | user10 |
| WS-012 | Logistics | Warehouse | Ubuntu 22.04 LTS | user12 |
| WS-015 | Production | Production Hall B | Windows 11 23H2 | user15 |
| WS-016 | Admin | Admin Building | Ubuntu 22.04 LTS | user16 |
| WS-018 | Production | Production Hall A | Windows 11 23H2 | user18 |
| WS-019 | QA | QA Lab | Windows 11 23H2 | user19 |

**Test phase:** pre-check (warranty, disk, backup), deploy, functional test (agent heartbeat, LIMS client start, print test).

**Acceptance criteria:** success rate of attempted machines at least 90%, at most 2 rollbacks, no open critical incident.

**Rollback steps:**
1. Stop the deployment job for the wave
2. Uninstall the new agent version via software deployment
3. Reinstall the previous approved version from the definitive software library
4. Verify agent heartbeat and functional test on each affected machine
5. Record deviation and rollback in the change record

**Go / no-go checklist:**
- [ ] Change record approved by change board (CHG number recorded)
- [ ] Previous wave acceptance criteria met
- [ ] Rollback package tested on a reference machine
- [ ] Backup of user profiles confirmed
- [ ] Service desk briefed and on standby
- [ ] No production campaign or audit scheduled in the window
- [ ] QA notified (learning project: no GxP release)

## Wave 3: Remaining plant workstations (18 machines)

| Host | Department | Location | OS | Owner |
|---|---|---|---|---|
| WS-020 | QA | QA Lab | Ubuntu 22.04 LTS | user20 |
| WS-021 | QA | QA Lab | Windows 11 23H2 | user21 |
| WS-022 | QA | QA Lab | Windows 11 23H2 | user22 |
| WS-023 | Production | Production Hall B | Windows 11 23H2 | user23 |
| WS-024 | QA | QA Lab | Ubuntu 22.04 LTS | user24 |
| WS-026 | QA | QA Lab | Windows 11 23H2 | user26 |
| WS-027 | Admin | Admin Building | Windows 11 23H2 | user27 |
| WS-028 | Admin | Admin Building | Ubuntu 22.04 LTS | user28 |
| WS-029 | Production | Production Hall B | Windows 11 23H2 | user29 |
| WS-030 | Production | Production Hall A | Windows 11 23H2 | user30 |
| WS-031 | Logistics | Warehouse | Windows 11 23H2 | user31 |
| WS-032 | QA | QA Lab | Ubuntu 22.04 LTS | user32 |
| WS-034 | Production | Production Hall A | Windows 11 23H2 | user34 |
| WS-035 | Admin | Admin Building | Windows 11 23H2 | user35 |
| WS-036 | Production | Production Hall B | Ubuntu 22.04 LTS | user36 |
| WS-037 | Admin | Admin Building | Windows 11 23H2 | user37 |
| WS-039 | Production | Production Hall A | Windows 11 23H2 | user39 |
| WS-040 | Logistics | Warehouse | Ubuntu 22.04 LTS | user40 |

**Test phase:** pre-check (warranty, disk, backup), deploy, functional test (agent heartbeat, LIMS client start, print test).

**Acceptance criteria:** success rate of attempted machines at least 90%, at most 2 rollbacks, no open critical incident.

**Rollback steps:**
1. Stop the deployment job for the wave
2. Uninstall the new agent version via software deployment
3. Reinstall the previous approved version from the definitive software library
4. Verify agent heartbeat and functional test on each affected machine
5. Record deviation and rollback in the change record

**Go / no-go checklist:**
- [ ] Change record approved by change board (CHG number recorded)
- [ ] Previous wave acceptance criteria met
- [ ] Rollback package tested on a reference machine
- [ ] Backup of user profiles confirmed
- [ ] Service desk briefed and on standby
- [ ] No production campaign or audit scheduled in the window
- [ ] QA notified (learning project: no GxP release)

## Excluded devices

| Host | Reason |
|---|---|
| WS-017 | retired |
| WS-025 | in_repair |
| WS-033 | retired |
| WS-038 | spare |
| SRV-01 | server |
| SRV-02 | server |
| SRV-03 | server |
| SRV-04 | server |
| SRV-05 | server |
| SRV-06 | server |
