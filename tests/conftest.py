import pytest

from inventory import store


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--hosts", default=None):
        skip = pytest.mark.skip(reason="infra tests need --hosts=local:// after the playbooks ran")
        for i in items:
            if "infra" in i.keywords:
                i.add_marker(skip)


@pytest.fixture(scope="session")
def devices():
    return store.generate()


@pytest.fixture
def con(tmp_path, devices):
    c = store.connect(tmp_path / "inv.db")
    for d in devices:
        store.add_device(c, {k: v for k, v in d.items() if k != "role"}, "test")
    yield c
    c.close()


@pytest.fixture
def yaml_file(tmp_path, devices):
    p = tmp_path / "devices.yaml"
    store.save_yaml(devices, p)
    return p
