"""Inventory CLI: generate, init, add, update, query, export, audit."""
import argparse
import getpass
import json
import sys

from inventory import store


def parser():
    p = argparse.ArgumentParser(prog="inventory", description=__doc__)
    p.add_argument("--db", default=str(store.DB_PATH))
    p.add_argument("--actor", default=None, help="name written to the audit log")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="write the simulated devices.yaml")
    g.add_argument("--seed", type=int, default=7)
    g.add_argument("--yaml", default=str(store.YAML_PATH))
    i = sub.add_parser("init", help="import devices.yaml into SQLite")
    i.add_argument("--yaml", default=str(store.YAML_PATH))
    a = sub.add_parser("add")
    for f in store.FIELDS:
        a.add_argument(f"--{f.replace('_', '-')}", dest=f, required=f in ("hostname", "type", "serial"))
    a.add_argument("--software", action="append", default=[], metavar="NAME=VERSION")
    u = sub.add_parser("update")
    u.add_argument("hostname")
    u.add_argument("--set", action="append", required=True, metavar="FIELD=VALUE",
                   help="field=value or software.<name>=<version> (empty value removes software)")
    q = sub.add_parser("query")
    for f in ("type", "status", "location", "os", "software"):
        q.add_argument(f"--{f}")
    q.add_argument("--warranty-before", dest="warranty_before")
    q.add_argument("--json", action="store_true")
    e = sub.add_parser("export")
    e.add_argument("--format", choices=["csv", "json", "yaml"], default="csv")
    e.add_argument("--out", required=True)
    au = sub.add_parser("audit")
    au.add_argument("--hostname")
    return p


def pairs(items):
    out = {}
    for item in items:
        if "=" not in item:
            raise store.InventoryError(f"expected KEY=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main(argv=None):
    a = parser().parse_args(argv)
    actor = a.actor or getpass.getuser()
    if a.cmd == "generate":
        store.save_yaml(store.generate(a.seed), a.yaml)
        print(f"wrote {a.yaml}")
        return 0
    con = store.connect(a.db)
    try:
        if a.cmd == "init":
            print(f"{store.import_yaml(con, a.yaml, actor)} devices imported")
        elif a.cmd == "add":
            dev = {f: getattr(a, f) for f in store.FIELDS if getattr(a, f) is not None}
            store.add_device(con, {**dev, "software": pairs(a.software)}, actor)
            print(f"added {a.hostname}")
        elif a.cmd == "update":
            print(f"{store.update_device(con, a.hostname, pairs(a.set), actor)} change(s) on {a.hostname}")
        elif a.cmd == "query":
            rows = store.query(con, a.type, a.status, a.location, a.os, a.software, a.warranty_before)
            if a.json:
                print(json.dumps(rows, indent=2))
            else:
                for d in rows:
                    print(f"{d['hostname']:8} {d['type']:12} {d['status']:10} {d['os']:20} {d['location']}")
                print(f"{len(rows)} device(s)")
        elif a.cmd == "export":
            print(f"exported {store.export(con, a.format, a.out)} devices to {a.out}")
        elif a.cmd == "audit":
            for r in store.audit_log(con, a.hostname):
                print(f"{r['ts']} {r['actor']} {r['action']} {r['hostname']} {r['field'] or ''} "
                      f"{r['old'] or ''} -> {r['new'] or ''}".rstrip())
    except store.InventoryError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
