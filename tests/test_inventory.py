import json

import pytest
import yaml

from inventory import store


def test_generates_40_workstations_and_6_servers(devices):
    types = [d["type"] for d in devices]
    assert types.count("workstation") == 40 and types.count("server") == 6


def test_generation_is_deterministic():
    assert store.generate(1) == store.generate(1) and store.generate(1) != store.generate(2)


def test_serials_and_hostnames_unique(devices):
    assert len({d["serial"] for d in devices}) == len({d["hostname"] for d in devices}) == 46


@pytest.mark.parametrize("field", store.FIELDS)
def test_every_device_has_field(devices, field):
    assert all(d.get(field) for d in devices)


def test_software_has_versions(devices):
    assert all(d["software"] and all(v for v in d["software"].values()) for d in devices)


def test_yaml_roundtrip(yaml_file, devices):
    assert store.load_yaml(yaml_file) == devices


def test_repo_yaml_matches_generator():
    assert store.load_yaml() == store.generate()


def test_import_into_sqlite(con):
    assert len(store.query(con)) == 46


def test_import_yaml_is_idempotent(tmp_path, yaml_file):
    c = store.connect(tmp_path / "x.db")
    assert store.import_yaml(c, yaml_file) == 46 and store.import_yaml(c, yaml_file) == 0


def test_add_is_audited(con):
    store.add_device(con, {"hostname": "WS-099", "type": "workstation", "serial": "NEW1"}, "alice")
    log = store.audit_log(con, "WS-099")
    assert log[0]["action"] == "add" and log[0]["actor"] == "alice"


def test_add_duplicate_rejected(con):
    with pytest.raises(store.InventoryError):
        store.add_device(con, {"hostname": "WS-001", "type": "workstation", "serial": "X"})


def test_add_duplicate_serial_rejected(con, devices):
    with pytest.raises(store.InventoryError):
        store.add_device(con, {"hostname": "WS-100", "type": "workstation", "serial": devices[0]["serial"]})


@pytest.mark.parametrize("dev", [{"hostname": "A", "type": "laptop", "serial": "1"},
                                 {"hostname": "A", "type": "server"},
                                 {"hostname": "A", "type": "server", "serial": "1", "status": "lost"},
                                 {"hostname": "A", "type": "server", "serial": "1", "warranty_end": "31.12.2026"}])
def test_add_validation(con, dev):
    with pytest.raises(store.InventoryError):
        store.add_device(con, dev)


def test_update_field_writes_old_and_new(con):
    old = store.get_device(con, "WS-002")["location"]
    assert store.update_device(con, "WS-002", {"location": "QA Lab 2"}, "bob") == 1
    entry = store.audit_log(con, "WS-002")[-1]
    assert (entry["field"], entry["old"], entry["new"], entry["actor"]) == ("location", old, "QA Lab 2", "bob")


def test_update_without_change_not_audited(con):
    before = len(store.audit_log(con))
    assert store.update_device(con, "WS-002", {"status": store.get_device(con, "WS-002")["status"]}) == 0
    assert len(store.audit_log(con)) == before


def test_update_software_set_and_remove(con):
    store.update_device(con, "WS-003", {"software.Endpoint Agent": "9.9.9"})
    store.update_device(con, "WS-003", {"software.7-Zip": ""})
    sw = store.get_device(con, "WS-003")["software"]
    actions = [a["action"] for a in store.audit_log(con, "WS-003")]
    assert sw["Endpoint Agent"] == "9.9.9" and "7-Zip" not in sw and {"set_software", "remove_software"} <= set(actions)


def test_update_unknown_device_or_field(con):
    with pytest.raises(store.InventoryError):
        store.update_device(con, "WS-999", {"status": "spare"})
    with pytest.raises(store.InventoryError):
        store.update_device(con, "WS-001", {"colour": "red"})


def test_query_filters(con):
    assert {d["type"] for d in store.query(con, type="server")} == {"server"}
    assert len(store.query(con, status="retired")) == 2
    assert all("Ubuntu" in d["os"] for d in store.query(con, os="Ubuntu"))
    assert all("PostgreSQL" in d["software"] for d in store.query(con, software="PostgreSQL"))
    assert all(d["warranty_end"] < "2026-01-01" for d in store.query(con, warranty_before="2026-01-01"))
    assert all(d["location"] == "Server Room" for d in store.query(con, location="Server Room"))


@pytest.mark.parametrize("fmt", ["csv", "json", "yaml"])
def test_export_formats(con, tmp_path, fmt):
    out = tmp_path / f"inv.{fmt}"
    assert store.export(con, fmt, out) == 46
    text = out.read_text()
    if fmt == "json":
        assert len(json.loads(text)) == 46
    elif fmt == "yaml":
        assert len(yaml.safe_load(text)["devices"]) == 46
    else:
        assert text.startswith("hostname,") and text.count("\n") == 47


def test_export_unknown_format(con, tmp_path):
    with pytest.raises(store.InventoryError):
        store.export(con, "xml", tmp_path / "x")
