# Evaluation report: software deployment tool (decision support, learning material)

Two generic options are compared for deploying software to the plant workstations. Option names are placeholders, not real products.

| Criterion | Weight | Option A: agent-based deployment suite | Option B: Ansible + scripts (this project) |
|---|---|---|---|
| Audit trail and reporting | 25 % | 5 | 3 |
| Windows and Linux support | 20 % | 4 | 4 |
| Cost (licences, effort) | 20 % | 2 | 5 |
| Integration with change control | 15 % | 4 | 3 |
| Skills available in the team | 10 % | 3 | 4 |
| Vendor support | 10 % | 5 | 2 |
| **Weighted score (1-5)** | 100 % | **3.90** | **3.65** |

Weighted score = sum(weight x score). Option A wins narrowly because audit trail and vendor support weigh more in a regulated environment. Recommendation: pilot Option A for Windows; keep Option B for Linux servers. Decision is up to the change board.
