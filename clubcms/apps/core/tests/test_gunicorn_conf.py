"""gunicorn.conf.py must load and keep the control socket disabled."""

from pathlib import Path

from gunicorn.config import Config

CONF = Path(__file__).resolve().parents[3] / "gunicorn.conf.py"


def test_gunicorn_conf_disables_control_socket():
    namespace = {}
    exec(compile(CONF.read_text(), str(CONF), "exec"), namespace)
    cfg = Config()
    for key, value in namespace.items():
        if key in cfg.settings:
            cfg.set(key, value)
    assert cfg.control_socket_disable is True
