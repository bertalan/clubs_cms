"""
Gunicorn settings shared by every environment that starts gunicorn from
this directory (systemd unit on live, docker-compose.prod.yml).

Gunicorn loads ./gunicorn.conf.py automatically; command-line flags in the
systemd unit still take precedence.
"""

# Gunicorn 26 opens a control socket under $HOME/.gunicorn by default. The
# service user's home is not writable by it, so startup logs
# "Control server error: Permission denied". The control interface is not
# used here: process management goes through systemd.
control_socket_disable = True
