"""Rollout planner and simulator: three waves of SIMULATED workstations, per-machine status, CSV/HTML report."""
import argparse
import csv
import html
import json
import random
import sys
from datetime import date
from pathlib import Path

from inventory import store

ROOT = Path(__file__).resolve().parent.parent
TARGET = {"name": "Endpoint Agent", "version": "2.3.0", "change": "CHG-2026-014"}
PHASES = ["pre_check", "deploy", "functional_test"]
ACCEPTANCE = 0.90
MAX_ROLLBACKS = 2
ROLLOUT_DATE = date(2026, 2, 2)
WAVE_NAMES = ["Pilot (IT and QA)", "Early adopters", "Remaining plant workstations"]


def eligible(devices):
    return sorted((d for d in devices if d["type"] == "workstation" and d["status"] == "active"),
                  key=lambda d: d["hostname"])


def build_plan(devices, pilot_size=6, wave2_share=0.4):
    el = eligible(devices)
    pilot = [d for d in el if d["department"] in ("IT", "QA")][:pilot_size]
    rest = [d for d in el if d not in pilot]
    n2 = round(len(rest) * wave2_share)
    groups = [pilot, rest[:n2], rest[n2:]]
    excluded = [{"hostname": d["hostname"], "reason": "server" if d["type"] == "server" else d["status"]}
                for d in devices if d not in el]
    return {"target": TARGET, "waves": [{"wave": i + 1, "name": WAVE_NAMES[i], "hosts": [d["hostname"] for d in g]}
                                         for i, g in enumerate(groups)], "excluded": excluded}


def run_machine(dev, wave, rng, failure_rate, rollout_date):
    r = {"hostname": dev["hostname"], "wave": wave, "status": "success", "failed_phase": "", "retries": 0,
         "rolled_back": False, "detail": ""}
    if dev["warranty_end"] < rollout_date.isoformat():
        return {**r, "status": "blocked", "failed_phase": "pre_check", "detail": "warranty expired"}
    for phase in PHASES:
        if rng.random() < failure_rate / len(PHASES):
            r["retries"] += 1
            if rng.random() < 0.5:
                continue
            if phase == "pre_check":
                return {**r, "status": "blocked", "failed_phase": phase, "detail": "pre-check failed twice"}
            return {**r, "status": "rolled_back", "failed_phase": phase, "rolled_back": True,
                    "detail": f"{phase} failed after retry, rollback executed"}
    return r


def simulate(plan, devices, seed=2026, failure_rate=0.12, rollout_date=ROLLOUT_DATE):
    rng, by_host = random.Random(seed), {d["hostname"]: d for d in devices}
    rows, waves, halted = [], [], False
    for w in plan["waves"]:
        if halted:
            rows += [{"hostname": h, "wave": w["wave"], "status": "on_hold", "failed_phase": "", "retries": 0,
                      "rolled_back": False, "detail": "previous wave no-go"} for h in w["hosts"]]
            waves.append({"wave": w["wave"], "name": w["name"], "machines": len(w["hosts"]), "decision": "not started"})
            continue
        res = [run_machine(by_host[h], w["wave"], rng, failure_rate, rollout_date) for h in w["hosts"]]
        rows += res
        count = lambda s: sum(r["status"] == s for r in res)
        attempted = len(res) - count("blocked")
        rate = round(count("success") / attempted, 3) if attempted else 0.0
        go = rate >= ACCEPTANCE and count("rolled_back") <= MAX_ROLLBACKS
        halted = not go
        waves.append({"wave": w["wave"], "name": w["name"], "machines": len(res), "success": count("success"),
                      "rolled_back": count("rolled_back"), "blocked": count("blocked"), "success_rate": rate,
                      "decision": "go" if go else "no-go"})
    done = [r for r in rows if r["status"] != "on_hold"]
    attempted = [r for r in done if r["detail"] != "warranty expired"]
    summary = {"devices": len(devices), "eligible": sum(len(w["hosts"]) for w in plan["waves"]),
               "excluded": len(plan["excluded"]), "waves": len(plan["waves"]),
               "waves_executed": sum(w["decision"] != "not started" for w in waves),
               "configured_failure_rate": failure_rate,
               "observed_failure_rate": round(sum(r["retries"] > 0 for r in attempted) / len(attempted), 3)
               if attempted else 0.0,
               "retries": sum(r["retries"] for r in done), "rollbacks": sum(r["rolled_back"] for r in done),
               "blocked": sum(r["status"] == "blocked" for r in done),
               "success": sum(r["status"] == "success" for r in done), "seed": seed}
    return {"summary": summary, "waves": waves, "machines": rows}


CHECKLIST = ["Change record approved by change board (CHG number recorded)", "Previous wave acceptance criteria met",
             "Rollback package tested on a reference machine", "Backup of user profiles confirmed",
             "Service desk briefed and on standby", "No production campaign or audit scheduled in the window",
             "QA notified (learning project: no GxP release)"]
ROLLBACK = ["Stop the deployment job for the wave", "Uninstall the new agent version via software deployment",
            "Reinstall the previous approved version from the definitive software library",
            "Verify agent heartbeat and functional test on each affected machine",
            "Record deviation and rollback in the change record"]


def render_plan(plan, devices):
    by = {d["hostname"]: d for d in devices}
    t = plan["target"]
    md = [f"# Rollout plan: {t['name']} {t['version']} ({t['change']})", "",
          "Learning project with simulated machines. Not GxP validated.", "",
          f"Eligible workstations: {sum(len(w['hosts']) for w in plan['waves'])}, excluded: {len(plan['excluded'])}"]
    for w in plan["waves"]:
        md += ["", f"## Wave {w['wave']}: {w['name']} ({len(w['hosts'])} machines)", "",
               "| Host | Department | Location | OS | Owner |", "|---|---|---|---|---|"]
        md += [f"| {h} | {by[h]['department']} | {by[h]['location']} | {by[h]['os']} | {by[h]['owner']} |"
               for h in w["hosts"]]
        md += ["", "**Test phase:** pre-check (warranty, disk, backup), deploy, functional test "
               "(agent heartbeat, LIMS client start, print test).", "",
               f"**Acceptance criteria:** success rate of attempted machines at least {ACCEPTANCE:.0%}, "
               f"at most {MAX_ROLLBACKS} rollbacks, no open critical incident.", "", "**Rollback steps:**"]
        md += [f"{i}. {s}" for i, s in enumerate(ROLLBACK, 1)]
        md += ["", "**Go / no-go checklist:**"] + [f"- [ ] {c}" for c in CHECKLIST]
    md += ["", "## Excluded devices", "", "| Host | Reason |", "|---|---|"]
    md += [f"| {e['hostname']} | {e['reason']} |" for e in plan["excluded"]]
    return "\n".join(md) + "\n"


def write_reports(result, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cols = ["hostname", "wave", "status", "failed_phase", "retries", "rolled_back", "detail"]
    with (out / "rollout_status.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(result["machines"])
    (out / "rollout_summary.json").write_text(json.dumps({"summary": result["summary"], "waves": result["waves"]},
                                                         indent=2))
    s = result["summary"]
    wave_rows = "".join(f"<tr><td>{w['wave']}</td><td>{html.escape(w['name'])}</td><td>{w['machines']}</td>"
                        f"<td>{w.get('success', '-')}</td><td>{w.get('rolled_back', '-')}</td>"
                        f"<td>{w.get('blocked', '-')}</td><td>{w.get('success_rate', '-')}</td>"
                        f"<td>{w['decision']}</td></tr>" for w in result["waves"])
    m_rows = "".join("<tr>" + "".join(f"<td>{html.escape(str(r[c]))}</td>" for c in cols) + "</tr>"
                     for r in result["machines"])
    (out / "rollout_report.html").write_text(
        "<html><head><meta charset='utf-8'><title>Rollout report</title></head><body>"
        "<h1>Rollout report (simulated machines, learning project, not GxP validated)</h1>"
        f"<p>Devices: {s['devices']} | Eligible: {s['eligible']} | Waves executed: {s['waves_executed']} of {s['waves']}"
        f" | Success: {s['success']} | Rollbacks: {s['rollbacks']} | Blocked: {s['blocked']}"
        f" | Observed failure rate: {s['observed_failure_rate']}</p>"
        "<h2>Waves</h2><table border='1'><tr><th>Wave</th><th>Name</th><th>Machines</th><th>Success</th>"
        f"<th>Rolled back</th><th>Blocked</th><th>Success rate</th><th>Decision</th></tr>{wave_rows}</table>"
        "<h2>Machines</h2><table border='1'><tr>" + "".join(f"<th>{c}</th>" for c in cols) +
        f"</tr>{m_rows}</table></body></html>")
    return out


def load_devices(db=None, yaml_path=None):
    if db:
        con = store.connect(db)
        try:
            return store.query(con)
        finally:
            con.close()
    return store.load_yaml(yaml_path or store.YAML_PATH)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db")
    p.add_argument("--yaml")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--failure-rate", type=float, default=0.12)
    p.add_argument("--out", default=str(ROOT / "reports" / "rollout"))
    p.add_argument("--plan-out", default=str(ROOT / "rollout" / "plans" / "rollout_plan.md"))
    a = p.parse_args(argv)
    devices = load_devices(a.db, a.yaml)
    plan = build_plan(devices)
    Path(a.plan_out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.plan_out).write_text(render_plan(plan, devices))
    result = simulate(plan, devices, a.seed, a.failure_rate)
    write_reports(result, a.out)
    print(json.dumps(result["summary"]))
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
