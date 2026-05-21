# uSipipo Backend - Systemd Deployment Guide

Production-ready systemd service configuration for deploying the uSipipo Backend API on Linux servers.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Python 3.13+** installed
- **PostgreSQL** database running
- **Redis** server running (for caching/sessions)
- **Virtual environment** created and dependencies installed
- **`.env` file** configured with all required environment variables

## 🚀 Quick Start

```bash
# 1. Navigate to deploy directory
cd /path/to/usipipo/apps/backend/deploy

# 2. Copy service file to systemd directory
sudo cp usipipo-backend.service /etc/systemd/system/usipipo-backend.service

# 3. Edit the service file (replace placeholders)
sudo nano /etc/systemd/system/usipipo-backend.service

# 4. Create logs directory
sudo mkdir -p /path/to/usipipo/apps/backend/logs
sudo chown <USER>:<GROUP> /path/to/usipipo/apps/backend/logs

# 5. Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable usipipo-backend
sudo systemctl start usipipo-backend

# 6. Verify status
sudo systemctl status usipipo-backend
```

## ⚙️ Configuration

### Required Placeholders

Open the service file and replace these placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `<SYSTEM_USER>` | Linux user to run the service | `mowgli`, `usipipo`, `www-data` |
| `<SYSTEM_GROUP>` | Linux group for the service | `mowgli`, `usipipo`, `www-data` |
| `<PATH_TO_USISIPO_BACKEND>` | Absolute path to backend directory | `/home/mowgli/usipipo/apps/backend` |

### Finding Your User/Group

```bash
# Get current user info
id

# Output example:
# uid=1000(mowgli) gid=1000(mowgli) groups=1000(mowgli),...
# Use: User=mowgli Group=mowgli
```

### Environment Variables

The service loads environment variables from the `.env` file. Ensure these are set:

```bash
# Minimum required variables
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/usipipo
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
```

See `example.env` in the root directory for all available options.

## 📖 Service Management Commands

### Basic Operations

```bash
# Start service
sudo systemctl start usipipo-backend

# Stop service
sudo systemctl stop usipipo-backend

# Restart service
sudo systemctl restart usipipo-backend

# Reload configuration (if supported)
sudo systemctl reload usipipo-backend

# Check status
sudo systemctl status usipipo-backend
```

### Enable/Disable on Boot

```bash
# Enable automatic start on boot
sudo systemctl enable usipipo-backend

# Disable automatic start on boot
sudo systemctl disable usipipo-backend
```

### Viewing Logs

```bash
# View all logs (paged)
sudo journalctl -u usipipo-backend

# View logs in real-time (follow mode)
sudo journalctl -u usipipo-backend -f

# View logs from last hour
sudo journalctl -u usipipo-backend --since "1 hour ago"

# View logs with timestamps
sudo journalctl -u usipipo-backend -o short-precise

# View only errors
sudo journalctl -u usipipo-backend -p err

# View last N lines
sudo journalctl -u usipipo-backend -n 100
```

## 🔒 Security Hardening

This service file includes production-ready security configurations:

| Setting | Purpose |
|---------|---------|
| `ProtectSystem=strict` | Makes filesystem read-only except `ReadWritePaths` |
| `ProtectHome=false` | Allows access to home directory (required for `/home/` deployments) |
| `PrivateTmp=true` | Isolates `/tmp` from other processes |
| `NoNewPrivileges=true` | Prevents privilege escalation |
| `ReadWritePaths` | Restricts write access to logs directory only |
| `LimitNOFILE=65536` | Sets file descriptor limit |
| `LimitNPROC=4096` | Sets process limit |

### Additional Hardening (Optional)

For enhanced security in production environments:

```ini
# Add to [Service] section

# Restrict network capabilities (if not needed)
# RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

# Enable seccomp filtering
# SystemCallFilter=@system-service

# Restrict kernel tunables
# ProtectKernelTunables=true
# ProtectKernelModules=true
# ProtectControlGroups=true

# Lock down personality syscall
# LockPersonality=true
```

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check detailed status
sudo systemctl status usipipo-backend -l

# Check journal logs
sudo journalctl -u usipipo-backend -n 50 --no-pager

# Validate service file syntax
sudo systemd-analyze verify /etc/systemd/system/usipipo-backend.service

# Test configuration reload
sudo systemctl daemon-reload
```

### Common Issues

#### "Address already in use"

```bash
# Find process using the port
sudo lsof -i :8001
# or
sudo ss -tlnp | grep 8001

# Kill the process
sudo kill <PID>

# Restart service
sudo systemctl restart usipipo-backend
```

#### "Permission denied" errors

```bash
# Verify user/group ownership
ls -la /path/to/usipipo/apps/backend

# Fix ownership
sudo chown -R <USER>:<GROUP> /path/to/usipipo/apps/backend

# Verify .env file permissions (should be 600)
chmod 600 /path/to/usipipo/apps/backend/.env
```

#### Database connection failures

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U <user> -d usipipo

# Verify DATABASE_URL in .env
cat /path/to/usipipo/apps/backend/.env | grep DATABASE_URL
```

#### Redis connection failures

```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping

# Verify REDIS_URL in .env
cat /path/to/usipipo/apps/backend/.env | grep REDIS_URL
```

### Service Restarts Continuously

```bash
# Check restart count
sudo systemctl status usipipo-backend | grep "restart"

# View recent crashes
sudo journalctl -u usipipo-backend -n 100 | grep -i "error\|exception"

# Temporarily disable auto-restart for debugging
sudo systemctl edit usipipo-backend
# Add: [Service]\nRestart=no
```

## 📊 Monitoring

### Check Resource Usage

```bash
# Memory and CPU usage
sudo systemctl status usipipo-backend

# Detailed resource usage
sudo systemd-cgtop

# Process tree
ps aux | grep uvicorn
```

### Health Check

```bash
# Test API endpoint
curl http://localhost:8001/health

# Check API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/health
```

## 🔄 Updates and Maintenance

### Deploying New Version

```bash
# 1. Stop the service
sudo systemctl stop usipipo-backend

# 2. Update code (git pull, rsync, etc.)
cd /path/to/usipipo/apps/backend
git pull

# 3. Update dependencies
source .venv/bin/activate
pip install -U -r requirements.txt
# or with uv
uv sync

# 4. Run migrations (if any)
alembic upgrade head

# 5. Start the service
sudo systemctl start usipipo-backend

# 6. Verify
sudo systemctl status usipipo-backend
curl http://localhost:8001/health
```

### Rollback

```bash
# 1. Stop service
sudo systemctl stop usipipo-backend

# 2. Revert code
cd /path/to/usipipo/apps/backend
git revert HEAD

# 3. Revert migrations (if needed)
alembic downgrade -1

# 4. Restart service
sudo systemctl start usipipo-backend
```

## 📝 Architecture Notes

### Process Model

```
systemd
  └── uvicorn (master process)
      ├── worker 1 (uvicorn worker)
      └── worker 2 (uvicorn worker)
```

The service runs with 2 workers by default. Adjust based on your server capacity:

```ini
# In usipipo-backend.service
# Rule of thumb: (2 x CPU cores) + 1
ExecStart=... --workers 4
```

### Graceful Shutdown

The service is configured for graceful shutdown:

1. Receives `SIGTERM` signal
2. Stops accepting new connections
3. Waits up to 30 seconds for in-flight requests
4. Terminates workers
5. Exits cleanly

This prevents dropped connections during deployments or restarts.

## 📚 References

- [systemd.exec(5) - Service configuration](https://www.freedesktop.org/software/systemd/man/systemd.exec.html)
- [systemd.service(5) - Unit configuration](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Uvicorn Deployment Documentation](https://www.uvicorn.org/deployment/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## 🆘 Support

For issues or questions:

1. Check logs: `sudo journalctl -u usipipo-backend -f`
2. Review documentation: https://github.com/uSipipo-Team/usipipo
3. Open an issue on GitHub
