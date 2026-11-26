from inventory import cli


def run(capsys, db, *args):
    code = cli.main(["--db", str(db), "--actor", "tester", *args])
    return code, capsys.readouterr()


def test_generate_and_init(capsys, tmp_path):
    y, db = tmp_path / "d.yaml", tmp_path / "i.db"
    assert run(capsys, db, "generate", "--yaml", str(y))[0] == 0
    code, out = run(capsys, db, "init", "--yaml", str(y))
    assert code == 0 and "46 devices imported" in out.out


def test_add_update_audit(capsys, tmp_path):
    db = tmp_path / "i.db"
    assert run(capsys, db, "add", "--hostname", "WS-200", "--type", "workstation", "--serial", "S200",
               "--status", "active", "--software", "7-Zip=24.8.0")[0] == 0
    code, out = run(capsys, db, "update", "WS-200", "--set", "status=spare", "--set", "software.7-Zip=25.0.0")
    assert code == 0 and "2 change(s)" in out.out
    out = run(capsys, db, "audit", "--hostname", "WS-200")[1].out
    assert "tester add WS-200" in out and "status active -> spare" in out


def test_query_text_and_json(capsys, tmp_path):
    db, y = tmp_path / "i.db", tmp_path / "d.yaml"
    run(capsys, db, "generate", "--yaml", str(y))
    run(capsys, db, "init", "--yaml", str(y))
    assert "6 device(s)" in run(capsys, db, "query", "--type", "server")[1].out
    assert '"hostname": "SRV-01"' in run(capsys, db, "query", "--type", "server", "--json")[1].out


def test_export_command(capsys, tmp_path):
    db, y = tmp_path / "i.db", tmp_path / "d.yaml"
    run(capsys, db, "generate", "--yaml", str(y))
    run(capsys, db, "init", "--yaml", str(y))
    out = tmp_path / "e.csv"
    assert "exported 46" in run(capsys, db, "export", "--format", "csv", "--out", str(out))[1].out and out.exists()


def test_errors_return_code_2(capsys, tmp_path):
    db = tmp_path / "i.db"
    code, out = run(capsys, db, "update", "WS-404", "--set", "status=spare")
    assert code == 2 and "not found" in out.err
    assert run(capsys, db, "update", "WS-404", "--set", "nonsense")[0] == 2
