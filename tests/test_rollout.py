import csv
import json

import pytest

from rollout import plan as rp


@pytest.fixture(scope="module")
def plan(devices):
    return rp.build_plan(devices)


def test_three_waves(plan):
    assert [w["wave"] for w in plan["waves"]] == [1, 2, 3]


def test_only_active_workstations(plan, devices):
    by = {d["hostname"]: d for d in devices}
    hosts = [h for w in plan["waves"] for h in w["hosts"]]
    assert hosts and all(by[h]["type"] == "workstation" and by[h]["status"] == "active" for h in hosts)


def test_no_machine_in_two_waves(plan):
    hosts = [h for w in plan["waves"] for h in w["hosts"]]
    assert len(hosts) == len(set(hosts))


def test_every_device_planned_or_excluded(plan, devices):
    n = sum(len(w["hosts"]) for w in plan["waves"]) + len(plan["excluded"])
    assert n == len(devices)


def test_pilot_is_it_and_qa(plan, devices):
    by = {d["hostname"]: d for d in devices}
    assert all(by[h]["department"] in ("IT", "QA") for h in plan["waves"][0]["hosts"])


def test_waves_grow(plan):
    sizes = [len(w["hosts"]) for w in plan["waves"]]
    assert sizes[0] < sizes[1] < sizes[2]


def test_excluded_reasons(plan):
    assert {e["reason"] for e in plan["excluded"]} == {"server", "retired", "in_repair", "spare"}


def test_plan_markdown_sections(plan, devices):
    md = rp.render_plan(plan, devices)
    for part in ("## Wave 1", "## Wave 3", "Acceptance criteria", "Rollback steps", "Go / no-go checklist",
                 "Not GxP validated", "## Excluded devices"):
        assert part in md


def test_simulation_is_deterministic(plan, devices):
    assert rp.simulate(plan, devices, seed=5) == rp.simulate(plan, devices, seed=5)


def test_every_machine_has_a_status(plan, devices):
    res = rp.simulate(plan, devices)
    assert len(res["machines"]) == res["summary"]["eligible"]
    assert {r["status"] for r in res["machines"]} <= {"success", "rolled_back", "blocked", "on_hold"}


def test_zero_failure_rate_all_go(plan, devices):
    res = rp.simulate(plan, devices, failure_rate=0.0)
    assert all(w["decision"] == "go" for w in res["waves"]) and res["summary"]["rollbacks"] == 0


def test_expired_warranty_is_blocked(plan, devices):
    res = rp.simulate(plan, devices, failure_rate=0.0)
    by = {d["hostname"]: d for d in devices}
    blocked = [r for r in res["machines"] if r["status"] == "blocked"]
    assert blocked and all(by[r["hostname"]]["warranty_end"] < rp.ROLLOUT_DATE.isoformat() for r in blocked)


def test_high_failure_rate_triggers_no_go_and_hold(plan, devices):
    res = rp.simulate(plan, devices, failure_rate=0.9)
    decisions = [w["decision"] for w in res["waves"]]
    assert "no-go" in decisions and decisions[-1] == "not started"
    assert any(r["status"] == "on_hold" for r in res["machines"])


def test_rollback_counted(plan, devices):
    res = rp.simulate(plan, devices, failure_rate=0.6, seed=1)
    assert res["summary"]["rollbacks"] == sum(r["rolled_back"] for r in res["machines"]) > 0


def test_reports_written(plan, devices, tmp_path):
    res = rp.simulate(plan, devices)
    rp.write_reports(res, tmp_path)
    rows = list(csv.DictReader((tmp_path / "rollout_status.csv").open()))
    assert len(rows) == len(res["machines"])
    assert json.loads((tmp_path / "rollout_summary.json").read_text())["summary"] == res["summary"]
    assert "not GxP validated" in (tmp_path / "rollout_report.html").read_text()


def test_main_from_db(con, tmp_path):
    db = con.execute("PRAGMA database_list").fetchone()[2]
    res = rp.main(["--db", db, "--out", str(tmp_path / "r"), "--plan-out", str(tmp_path / "plan.md")])
    assert res["summary"]["devices"] == 46 and (tmp_path / "plan.md").exists()


def test_main_from_yaml(yaml_file, tmp_path):
    res = rp.main(["--yaml", str(yaml_file), "--out", str(tmp_path / "r"), "--plan-out", str(tmp_path / "p.md")])
    assert res["summary"]["waves"] == 3
