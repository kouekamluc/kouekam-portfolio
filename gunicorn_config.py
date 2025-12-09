"""
Gunicorn configuration file for production deployment.
Usage: gunicorn -c gunicorn_config.py kouekam_hub.wsgi:application
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'kouekam_hub'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Performance
max_requests = 1000
max_requests_jitter = 50
preload_app = True

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting kouekam_hub server")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down: Master")

