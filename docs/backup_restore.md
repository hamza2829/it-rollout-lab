# Backup and restore (simulated)

| System | What | Frequency | Retention | Restore test |
|---|---|---|---|---|
| SRV-01 file | user shares | daily incremental, weekly full | 30 days / 12 weeks | monthly, one folder |
| SRV-02 lims-db | PostgreSQL dump + WAL | hourly WAL, daily dump | 35 days | quarterly, full restore to test VM |
| SRV-04 backup | backup catalogue | daily | 90 days | yearly |
| Workstations | user profile | before every rollout wave | until wave closed | sample of 2 per wave |

Restore procedure: 1. open incident and CHG, 2. identify restore point, 3. restore to an isolated location, 4. verify checksums and application start, 5. move into production after owner approval, 6. document in the change record.
