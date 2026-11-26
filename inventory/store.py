"""YAML + SQLite inventory for SIMULATED devices, with an audit log of every change."""
import csv
import json
import os
import random
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
YAML_PATH = HERE / "devices.yaml"
DB_PATH = Path(os.getenv("INVENTORY_DB", HERE / "inventory.db"))
FIELDS = ["hostname", "type", "manufacturer", "model", "serial", "os", "owner", "department", "location",
          "status", "warranty_end"]
TYPES = {"workstation", "server"}
STATUSES = {"active", "in_repair", "spare", "retired"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (hostname TEXT PRIMARY KEY, type TEXT NOT NULL, manufacturer TEXT, model TEXT,
  serial TEXT UNIQUE NOT NULL, os TEXT, owner TEXT, department TEXT, location TEXT, status TEXT, warranty_end TEXT);
CREATE TABLE IF NOT EXISTS software (hostname TEXT REFERENCES devices(hostname) ON DELETE CASCADE, name TEXT,
  version TEXT, PRIMARY KEY (hostname, name));
CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, actor TEXT, action TEXT,
  hostname TEXT, field TEXT, old TEXT, new TEXT);
"""
LATEST = {"Endpoint Agent": "2.3.0", "LIMS Client": "4.3.1", "SAP GUI": "8.0.0", "7-Zip": "24.8.0",
          "PDF Reader": "24.2.0", "Office Suite": "16.0.17928"}
OLDER = {"Endpoint Agent": "2.1.4", "LIMS Client": "4.2.0", "SAP GUI": "7.70.0", "7-Zip": "23.1.0",
         "PDF Reader": "23.8.0", "Office Suite": "16.0.16731"}
WS_MODELS = [("Dell", "Latitude 5440"), ("HP", "EliteBook 840 G10"), ("Lenovo", "ThinkPad T14 Gen 4"),
             ("Dell", "OptiPlex 7010")]
PLACES = [("IT", "IT Office"), ("QA", "QA Lab"), ("Production", "Production Hall A"),
          ("Production", "Production Hall B"), ("Logistics", "Warehouse"), ("Admin", "Admin Building")]
SERVERS = [("file", "Ubuntu 22.04 LTS", {"Backup Agent": "12.1", "Node Exporter": "1.8.1"}),
           ("lims-db", "Ubuntu 24.04 LTS", {"PostgreSQL": "16.2", "Backup Agent": "12.1", "Node Exporter": "1.7.0"}),
           ("monitoring", "Ubuntu 24.04 LTS", {"Prometheus": "2.51.0", "Node Exporter": "1.8.1"}),
           ("backup", "Ubuntu 22.04 LTS", {"Backup Server": "12.1", "Node Exporter": "1.7.0"}),
           ("directory", "Windows Server 2022", {"Backup Agent": "11.0", "Endpoint Agent": "2.3.0"}),
           ("print", "Windows Server 2022", {"Backup Agent": "12.1", "Endpoint Agent": "2.1.4"})]


class InventoryError(Exception):
    pass


def generate(seed=7):
    """40 workstations and 6 servers, deterministic for a given seed. All values are invented."""
    rng, devices = random.Random(seed), []
    for i in range(1, 41):
        man, model = rng.choice(WS_MODELS)
        dept, loc = rng.choice(PLACES)
        status = "retired" if i in (17, 33) else "in_repair" if i == 25 else "spare" if i == 38 else "active"
        os_name = "Ubuntu 22.04 LTS" if i % 4 == 0 else "Windows 11 23H2"
        sw = {n: (LATEST[n] if rng.random() < 0.55 else OLDER[n]) for n in LATEST}
        if os_name.startswith("Ubuntu"):
            sw.pop("Office Suite")
            sw.pop("SAP GUI")
        devices.append({"hostname": f"WS-{i:03d}", "type": "workstation", "manufacturer": man, "model": model,
                        "serial": f"{man[:2].upper()}{1000000 + i * 7919}", "os": os_name, "owner": f"user{i:02d}",
                        "department": dept, "location": loc, "status": status,
                        "warranty_end": (date(2025, 3, 1) + timedelta(days=rng.randint(0, 1600))).isoformat(),
                        "software": sw})
    for j, (role, os_name, sw) in enumerate(SERVERS, 1):
        devices.append({"hostname": f"SRV-{j:02d}", "type": "server", "manufacturer": "Dell" if j % 2 else "HPE",
                        "model": "PowerEdge R650" if j % 2 else "ProLiant DL380 Gen11",
                        "serial": f"SV{2000000 + j * 104729}", "os": os_name, "owner": "it-ops", "department": "IT",
                        "location": "Server Room", "status": "active",
                        "warranty_end": (date(2026, 6, 30) + timedelta(days=200 * j)).isoformat(),
                        "software": dict(sw), "role": role})
    return devices


def save_yaml(devices, path=YAML_PATH):
    Path(path).write_text(yaml.safe_dump({"devices": devices}, sort_keys=False))


def load_yaml(path=YAML_PATH):
    return yaml.safe_load(Path(path).read_text())["devices"]


def connect(path=None):
    con = sqlite3.connect(str(path or DB_PATH))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    return con


def _audit(con, actor, action, hostname, field=None, old=None, new=None):
    con.execute("INSERT INTO audit (ts, actor, action, hostname, field, old, new) VALUES (?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), actor, action, hostname, field,
                 None if old is None else str(old), None if new is None else str(new)))


def _check(field, value):
    if field == "type" and value not in TYPES:
        raise InventoryError(f"invalid type {value!r}")
    if field == "status" and value not in STATUSES:
        raise InventoryError(f"invalid status {value!r}")
    if field == "warranty_end" and value:
        try:
            date.fromisoformat(str(value))
        except ValueError:
            raise InventoryError(f"invalid date {value!r}") from None


def get_device(con, hostname):
    row = con.execute("SELECT * FROM devices WHERE hostname = ?", (hostname,)).fetchone()
    if row is None:
        return None
    sw = con.execute("SELECT name, version FROM software WHERE hostname = ? ORDER BY name", (hostname,)).fetchall()
    return {**dict(row), "software": {r["name"]: r["version"] for r in sw}}


def add_device(con, dev, actor="system"):
    for f in ("hostname", "type", "serial"):
        if not dev.get(f):
            raise InventoryError(f"missing required field {f}")
    for f in FIELDS:
        _check(f, dev.get(f))
    if get_device(con, dev["hostname"]):
        raise InventoryError(f"device {dev['hostname']} already exists")
    try:
        con.execute(f"INSERT INTO devices ({','.join(FIELDS)}) VALUES ({','.join('?' * len(FIELDS))})",
                    [dev.get(f) for f in FIELDS])
    except sqlite3.IntegrityError as e:
        raise InventoryError(str(e)) from None
    for name, version in (dev.get("software") or {}).items():
        con.execute("INSERT INTO software VALUES (?,?,?)", (dev["hostname"], name, str(version)))
    _audit(con, actor, "add", dev["hostname"])
    con.commit()


def update_device(con, hostname, changes, actor="system"):
    """Apply field or software.<name> changes. Every real change is written to the audit log."""
    dev = get_device(con, hostname)
    if dev is None:
        raise InventoryError(f"device {hostname} not found")
    changed = 0
    for key, value in changes.items():
        if key.startswith("software."):
            name, old = key.split(".", 1)[1], dev["software"].get(key.split(".", 1)[1])
            if value in ("", None):
                if old is None:
                    continue
                con.execute("DELETE FROM software WHERE hostname = ? AND name = ?", (hostname, name))
                _audit(con, actor, "remove_software", hostname, name, old, None)
            elif old != value:
                con.execute("INSERT OR REPLACE INTO software VALUES (?,?,?)", (hostname, name, value))
                _audit(con, actor, "set_software", hostname, name, old, value)
            else:
                continue
            changed += 1
        elif key in FIELDS and key != "hostname":
            _check(key, value)
            if dev[key] != value:
                con.execute(f"UPDATE devices SET {key} = ? WHERE hostname = ?", (value, hostname))
                _audit(con, actor, "update", hostname, key, dev[key], value)
                changed += 1
        else:
            raise InventoryError(f"unknown field {key}")
    con.commit()
    return changed


def query(con, type=None, status=None, location=None, os=None, software=None, warranty_before=None):
    sql, params = "SELECT hostname FROM devices WHERE 1=1", []
    for col, val in (("type", type), ("status", status), ("location", location)):
        if val:
            sql += f" AND {col} = ?"
            params.append(val)
    if os:
        sql += " AND os LIKE ?"
        params.append(f"%{os}%")
    if software:
        sql += " AND hostname IN (SELECT hostname FROM software WHERE name = ?)"
        params.append(software)
    if warranty_before:
        sql += " AND warranty_end < ?"
        params.append(warranty_before)
    return [get_device(con, r["hostname"]) for r in con.execute(sql + " ORDER BY hostname", params)]


def import_yaml(con, path=None, actor="import"):
    added = 0
    for d in load_yaml(path or YAML_PATH):
        if not get_device(con, d["hostname"]):
            add_device(con, {k: v for k, v in d.items() if k in FIELDS or k == "software"}, actor)
            added += 1
    return added


def export(con, fmt, out):
    devices, out = query(con), Path(out)
    if fmt == "csv":
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS + ["software"])
            w.writeheader()
            for d in devices:
                w.writerow({**d, "software": ";".join(f"{k}={v}" for k, v in d["software"].items())})
    elif fmt == "json":
        out.write_text(json.dumps(devices, indent=2))
    elif fmt == "yaml":
        out.write_text(yaml.safe_dump({"devices": devices}, sort_keys=False))
    else:
        raise InventoryError(f"unknown format {fmt}")
    return len(devices)


def audit_log(con, hostname=None):
    sql, params = "SELECT * FROM audit", []
    if hostname:
        sql, params = sql + " WHERE hostname = ?", [hostname]
    return [dict(r) for r in con.execute(sql + " ORDER BY id", params)]
