# IT Rollout Lab

IT infrastructure and rollout project for a **simulated** pharma-style plant: inventory with audit log, Ansible configuration, PowerShell tooling, a three-wave rollout simulation and pharma-style process documentation. Portfolio project for an IT working student role.

```mermaid
flowchart LR
  Y[inventory/devices.yaml<br/>40 workstations, 6 servers] --> CLI[inventory CLI<br/>add, update, query, export]
  CLI --> DB[(SQLite + audit log)]
  DB --> PLAN[rollout/plan.py<br/>3 waves, go/no-go]
  PLAN --> REP[rollout report<br/>CSV + HTML]
  ANS[ansible/<br/>Linux workstation + server<br/>Windows playbook] --> RUN[GitHub runner] --> TI[Testinfra]
  PS[powershell/<br/>update check, users, inventory, health] --> PES[Pester on pwsh]
  DOCS[docs/<br/>change control, IQ/OQ/PQ, roles, backup, evaluation]
```

## Results

| Metric | Value |
|---|---|
| Simulated devices | 46 (40 workstations, 6 servers) |
| Eligible / excluded for rollout | 36 / 10 (servers, retired, in repair, spare) |
| Waves (pilot / early / rest) | 6 / 12 / 18 machines, all 3 waves go |
| Configured / observed failure rate | 0.12 / 0.103 (seed 2026) |
| Success / rollbacks / blocked | 27 / 2 / 7 (blocked = warranty expired) |
| Python pytest | 57 passed, 16 skipped (73 collected) |
| Python line coverage | 98.54 % (85 % gate) |
| Testinfra | 16 passed |
| Pester | 14 passed |
| ansible-lint | 11 files, 0 failures, 0 warnings (production profile passed) |

The pytest run skips the 16 infra-marked cases unless run after the Ansible playbooks; the dedicated Testinfra job ran all 16 successfully. The results above were recorded from the successful GitHub Actions run [45817068449](https://github.com/hamza2829/it-rollout-lab/actions/runs/45817068449). The rollout numbers come from the simulator with the default seed.

## Run

```bash
pip install -r requirements.txt
python -m inventory.cli init && python -m inventory.cli query --type server
python -m rollout.plan --out reports/rollout
pytest --cov
```

## Honest notes

- **All machines, users and data are simulated.** Hostnames, serials, owners and software versions are generated.
- **No real Windows host**: the Windows playbook is only linted and syntax-checked. PowerShell scripts run on pwsh on Linux against JSON fixtures.
- The Linux playbooks really run, but on the GitHub Actions runner, not on plant machines.
- **No real pharma environment. Not GxP validated.** IQ/OQ/PQ checklists and change control are learning material.
- **No real Azure** or other cloud resources are used.
