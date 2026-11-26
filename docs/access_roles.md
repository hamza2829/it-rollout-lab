# Access rights and user roles (simulated)

| Role | Linux group | Windows group | Rights |
|---|---|---|---|
| Lab administrator | labadmins | Administrators | sudo, install software, manage users |
| Operator | laboperators | LabOperators | run applications, no admin rights |
| QA reviewer | - | LabQA | read reports and audit logs |
| IT service account | - | - | Ansible deployment only, key-based |

Principles: least privilege, named accounts only (no shared logins), quarterly access review against the inventory owner field, leavers removed on the last working day.
