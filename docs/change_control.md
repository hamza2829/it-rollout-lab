# Change control (learning material, not GxP validated)

| Step | Owner | Output |
|---|---|---|
| 1. Change request | Requester | CHG record with description, reason, affected systems from the inventory |
| 2. Impact and risk assessment | IT + system owner | Risk class (low / medium / high), GxP relevance, affected waves |
| 3. Approval | Change board, QA for GxP-relevant changes | Signed approval, planned window |
| 4. Test in pilot | IT | Pilot wave results, deviations |
| 5. Implementation | IT | Waves executed, per machine status (`rollout_status.csv`) |
| 6. Verification | IT + key users | Acceptance criteria met, go/no-go record per wave |
| 7. Closure | Change owner | Final report, inventory updated, audit log reviewed |

Rules: no change without a CHG number, emergency changes are documented within 24 h, every inventory change is recorded in the audit log (who, when, old value, new value).
