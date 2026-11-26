"""Testinfra checks run on the GitHub runner after the Linux playbooks (local backend)."""
import pytest

pytestmark = pytest.mark.infra


@pytest.mark.parametrize("pkg", ["curl", "chrony", "unattended-upgrades", "openssh-server", "ufw",
                                 "prometheus-node-exporter", "rsync"])
def test_packages_installed(host, pkg):
    assert host.package(pkg).is_installed


@pytest.mark.parametrize("user,group", [("labadmin", "labadmins"), ("operator01", "laboperators")])
def test_users_and_groups(host, user, group):
    assert host.user(user).exists and group in host.user(user).groups


def test_sudoers_for_admins(host):
    f = host.file("/etc/sudoers.d/labadmins")
    assert f.exists and f.mode == 0o440 and f.contains("%labadmins")


@pytest.mark.parametrize("line", ["PermitRootLogin no", "PasswordAuthentication no", "MaxAuthTries 3"])
def test_ssh_hardening(host, line):
    assert host.file("/etc/ssh/sshd_config.d/10-hardening.conf").contains(line)


def test_firewall_active(host):
    out = host.check_output("sudo ufw status verbose")
    assert "Status: active" in out and "deny (incoming)" in out and "22/tcp" in out


def test_auto_updates_enabled(host):
    assert host.file("/etc/apt/apt.conf.d/20auto-upgrades").contains('Unattended-Upgrade "1"')


def test_monitoring_agent_running(host):
    s = host.service("prometheus-node-exporter")
    assert s.is_running and s.is_enabled
    assert host.socket("tcp://0.0.0.0:9100").is_listening or host.socket("tcp://:::9100").is_listening
